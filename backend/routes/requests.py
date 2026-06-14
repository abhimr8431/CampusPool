from flask import Blueprint, request, jsonify, current_app
import logging
from bson import ObjectId
from datetime import datetime
from models.db import rides, users, requests as req_col
from models.request import request_schema, accept_request, RequestAcceptError
from middleware.auth import token_required
from algorithms.matching import calculate_fare, haversine

requests_bp = Blueprint('requests', __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

COLLEGE_LAT = 13.0128
COLLEGE_LON = 77.5748


def serialize_req(r):
    r['_id']          = str(r['_id'])
    r['ride_id']      = str(r['ride_id'])
    r['passenger_id'] = str(r['passenger_id'])
    return r


# ── PASSENGER: SEND RIDE REQUEST ──────────────
@requests_bp.route('/send', methods=['POST'])
@token_required
def send_request(current_user):
    data    = request.get_json()
    logger.debug('send_request called by user %s with payload %s', str(current_user.get('_id')), data)
    ride_id = data.get('ride_id')
    if not ride_id:
        return jsonify({'error': 'ride_id required'}), 400

    ride = rides.find_one({'_id': ObjectId(ride_id)})
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    if ride['status'] != 'open':
        return jsonify({'error': 'Ride is no longer available'}), 400
    if ride['seats_left'] <= 0:
        return jsonify({'error': 'Ride is full'}), 400
    if str(ride['rider_id']) == str(current_user['_id']):
        return jsonify({'error': 'You cannot request your own ride'}), 400

    # Check if already requested
    existing = req_col.find_one({
        'ride_id':      ObjectId(ride_id),
        'passenger_id': current_user['_id'],
        'status':       {'$in': ['pending', 'accepted']}
    })
    if existing:
        return jsonify({'error': 'You already have an active request for this ride'}), 400

    # Calculate fare for this specific passenger pickup location
    p_lat = float(data.get('passenger_lat', ride['origin']['lat']))
    p_lon = float(data.get('passenger_lon', ride['origin']['lon']))
    route_dist = (haversine(ride['origin']['lat'], ride['origin']['lon'], p_lat, p_lon) +
                  haversine(p_lat, p_lon, COLLEGE_LAT, COLLEGE_LON))
    fare = calculate_fare(route_dist, ride['mileage_kmpl'], ride['fuel_type'])

    new_req = request_schema(ride_id, str(current_user['_id']))
    new_req['passenger_lat']  = p_lat
    new_req['passenger_lon']  = p_lon
    new_req['fare']           = fare
    result = req_col.insert_one(new_req)
    logger.info('Created request %s for ride %s by passenger %s', str(result.inserted_id), ride_id, str(current_user.get('_id')))

    # Notify rider via Socket.io
    try:
        from app import socketio
        socketio.emit(f'new_request_{str(ride["rider_id"])}', {
            'request_id':     str(result.inserted_id),
            'passenger_name': current_user['name'],
            'passenger_year': current_user.get('year', ''),
            'passenger_branch': current_user.get('branch', ''),
            'verified':       current_user['verification']['is_verified'],
            'fare':           fare,
            'expires_in_mins': 15
        })
    except Exception as e:
        logger.exception('Socket notify failed while sending new_request event')

    return jsonify({
        'message':    'Request sent. Waiting for rider to confirm.',
        'request_id': str(result.inserted_id),
        'fare':       fare,
        'expires_in': '15 minutes'
    }), 201


# ── RIDER: ACCEPT REQUEST ─────────────────────
@requests_bp.route('/<req_id>/accept', methods=['PATCH'])
@token_required
def accept_request(current_user, req_id):
    req  = req_col.find_one({'_id': ObjectId(req_id)})
    logger.debug('accept_request called: req_id=%s by user=%s', req_id, str(current_user.get('_id')))
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    ride = rides.find_one({'_id': req['ride_id']})
    if str(ride['rider_id']) != str(current_user['_id']):
        return jsonify({'error': 'Not your ride'}), 403
    if req['status'] != 'pending':
        return jsonify({'error': f'Request is already {req["status"]}'}), 400
    if datetime.utcnow() > req['expires_at']:
        req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'expired'}})
        return jsonify({'error': 'Request has expired'}), 400

    # Accept and reduce seat count
    # Perform update atomically and read back ride to verify seats
    req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'accepted'}})
    update_result = rides.update_one({'_id': req['ride_id'], 'seats_left': {'$gt': 0}},
                                     {'$inc': {'seats_left': -1},
                                      '$push': {'passengers': req['passenger_id']}})
    if update_result.modified_count == 0:
        # Seat update failed (possibly race or no seats left) — revert request
        req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'declined'}})
        logger.warning('Failed to decrement seats for ride %s; request %s reverted', str(req['ride_id']), req_id)
        return jsonify({'error': 'Failed to accept request — ride may be full'}), 400
    logger.info('Request %s accepted; decremented seats for ride %s', req_id, str(req['ride_id']))

    # Mark ride full if no seats left
    updated_ride = rides.find_one({'_id': req['ride_id']})
    if updated_ride['seats_left'] == 0:
        rides.update_one({'_id': req['ride_id']}, {'$set': {'status': 'full'}})

    # Notify passenger via Socket.io
    try:
        from app import socketio
        socketio.emit(f'request_accepted_{str(req["passenger_id"])}', {
            'ride_id':        str(req['ride_id']),
            'rider_name':     current_user['name'],
            'rider_phone':    current_user.get('phone', ''),
            'vehicle':        current_user.get('vehicle', {}).get('name', ''),
            'fare':           req.get('fare', {}),
            'message':        f'{current_user["name"]} accepted your ride request!'
        })
    except Exception as e:
        logger.exception('Socket notify failed while sending request_accepted event')

    return jsonify({'message': 'Request accepted', 'fare': req.get('fare', {})})


# ── RIDER: DECLINE REQUEST ────────────────────
@requests_bp.route('/<req_id>/decline', methods=['PATCH'])
@token_required
def decline_request(current_user, req_id):
    req  = req_col.find_one({'_id': ObjectId(req_id)})
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    ride = rides.find_one({'_id': req['ride_id']})
    if str(ride['rider_id']) != str(current_user['_id']):
        return jsonify({'error': 'Not your ride'}), 403

    req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'declined'}})

    # Notify passenger
    try:
        from app import socketio
        socketio.emit(f'request_declined_{str(req["passenger_id"])}', {
            'message': f'{current_user["name"]} declined your request. Try another ride.'
        })
    except Exception as e:
        print(f'Socket notify failed: {e}')

    return jsonify({'message': 'Request declined'})


# ── GET MY INCOMING REQUESTS (rider sees pending) ──
@requests_bp.route('/incoming', methods=['GET'])
@token_required
def incoming_requests(current_user):
    # Get all rides by this rider
    my_rides = list(rides.find({'rider_id': current_user['_id']}))
    ride_ids = [r['_id'] for r in my_rides]

    # Find pending requests for those rides
    pending = list(req_col.find({
        'ride_id': {'$in': ride_ids},
        'status':  'pending'
    }))
    result = []
    for r in pending:
        passenger = users.find_one({'_id': r['passenger_id']},
                                   {'password': 0, 'otp': 0})
        ride      = rides.find_one({'_id': r['ride_id']})
        result.append({
            'request_id':     str(r['_id']),
            'status':         r['status'],
            'fare':           r.get('fare', {}),
            'expires_at':     r['expires_at'].isoformat(),
            'passenger': {
                'id':       str(passenger['_id']),
                'name':     passenger['name'],
                'year':     passenger.get('year', ''),
                'branch':   passenger.get('branch', ''),
                'rating':   passenger.get('rating', 5.0),
                'verified': passenger['verification']['is_verified']
            },
            'ride': {
                'id':             str(ride['_id']),
                'departure_time': ride['departure_time'],
                'origin':         ride['origin']
            }
        })
    return jsonify({'requests': result, 'count': len(result)})


# ── GET MY SENT REQUESTS (passenger tracks) ───
@requests_bp.route('/my-requests', methods=['GET'])
@token_required
def my_requests(current_user):
    requests_list = list(req_col.find({
        'passenger_id': current_user['_id'],
        'status': {'$in': ['pending', 'accepted']}
    }))

    result = []
    for r in requests_list:
        ride = rides.find_one({'_id': r['ride_id']})
        rider = users.find_one({'_id': ride['rider_id']}, {'password': 0, 'otp': 0})
        result.append({
            'request_id': str(r['_id']),
            'status':      r['status'],
            'fare':        r.get('fare', {}),
            'pickup': {
                'lat': r.get('passenger_lat'),
                'lon': r.get('passenger_lon')
            },
            'ride': {
                'id':             str(ride['_id']),
                'departure_time': ride['departure_time'],
                'origin':         ride['origin'],
                'vehicle_name':   ride.get('vehicle_name'),
                'seats_left':     ride.get('seats_left')
            },
            'rider': {
                'id':       str(rider['_id']),
                'name':     rider['name'],
                'year':     rider.get('year', ''),
                'branch':   rider.get('branch', ''),
                'rating':   rider.get('rating', 5.0),
                'verified': rider['verification']['is_verified']
            }
        })

    return jsonify({'requests': result, 'count': len(result)})


# ── GET ACTIVE ACCEPTED REQUESTS (passenger + rider) ───
@requests_bp.route('/active', methods=['GET'])
@token_required
def active_requests(current_user):
    active = []

    passenger_accepted = list(req_col.find({
        'passenger_id': current_user['_id'],
        'status': 'accepted'
    }))
    for r in passenger_accepted:
        ride = rides.find_one({'_id': r['ride_id']})
        rider = users.find_one({'_id': ride['rider_id']}, {'password': 0, 'otp': 0})
        active.append({
            'request_id': str(r['_id']),
            'status': r['status'],
            'role': 'passenger',
            'fare': r.get('fare', {}),
            'pickup': {
                'lat': r.get('passenger_lat'),
                'lon': r.get('passenger_lon')
            },
            'ride': {
                'id':             str(ride['_id']),
                'departure_time': ride['departure_time'],
                'origin':         ride['origin'],
                'vehicle_name':   ride.get('vehicle_name'),
                'seats_left':     ride.get('seats_left')
            },
            'rider': {
                'id':       str(rider['_id']),
                'name':     rider['name'],
                'year':     rider.get('year', ''),
                'branch':   rider.get('branch', ''),
                'rating':   rider.get('rating', 5.0),
                'verified': rider['verification']['is_verified']
            }
        })

    my_rides = list(rides.find({'rider_id': current_user['_id']}))
    ride_ids = [r['_id'] for r in my_rides]
    rider_accepted = list(req_col.find({
        'ride_id': {'$in': ride_ids},
        'status': 'accepted'
    }))
    for r in rider_accepted:
        passenger = users.find_one({'_id': r['passenger_id']}, {'password': 0, 'otp': 0})
        ride = rides.find_one({'_id': r['ride_id']})
        active.append({
            'request_id': str(r['_id']),
            'status': r['status'],
            'role': 'rider',
            'fare': r.get('fare', {}),
            'pickup': {
                'lat': r.get('passenger_lat'),
                'lon': r.get('passenger_lon')
            },
            'ride': {
                'id':             str(ride['_id']),
                'departure_time': ride['departure_time'],
                'origin':         ride['origin'],
                'vehicle_name':   ride.get('vehicle_name'),
                'seats_left':     ride.get('seats_left')
            },
            'passenger': {
                'id':       str(passenger['_id']),
                'name':     passenger['name'],
                'year':     passenger.get('year', ''),
                'branch':   passenger.get('branch', ''),
                'rating':   passenger.get('rating', 5.0),
                'verified': passenger['verification']['is_verified']
            }
        })

    return jsonify({'active_requests': active, 'count': len(active)})
