from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from models.db import rides, users
from models.ride import ride_schema
from middleware.auth import token_required
from algorithms.matching import find_nearby_rides, calculate_fare, haversine

rides_bp = Blueprint('rides', __name__)

COLLEGE_LAT = 13.0128
COLLEGE_LON = 77.5748
COLLEGE_NAME = 'Ramaiah Institute of Technology'


def serialize_ride(ride):
    """Convert MongoDB ride doc to JSON-safe dict."""
    ride['_id']      = str(ride['_id'])
    ride['rider_id'] = str(ride['rider_id'])
    return ride


# ── POST A RIDE (rider offers a ride) ─────────
@rides_bp.route('/post', methods=['POST'])
@token_required
def post_ride(current_user):
    data = request.get_json()

    required = ['origin_lat', 'origin_lon', 'origin_name', 'departure_time']
    for f in required:
        if f not in data:
            return jsonify({'error': f'{f} is required'}), 400

    vehicle = current_user.get('vehicle', {})
    if not vehicle.get('mileage_kmpl') or float(vehicle.get('mileage_kmpl', 0)) <= 0:
        return jsonify({'error': 'Please set your vehicle mileage in profile first'}), 400

    new_ride = ride_schema(
        rider_id     = str(current_user['_id']),
        origin_lat   = float(data['origin_lat']),
        origin_lon   = float(data['origin_lon']),
        origin_name  = data['origin_name'],
        college_lat  = COLLEGE_LAT,
        college_lon  = COLLEGE_LON,
        college_name = COLLEGE_NAME,
        departure_time = data['departure_time'],
        vehicle_name   = vehicle.get('name', ''),
        mileage_kmpl   = vehicle.get('mileage_kmpl', 40),
        fuel_type      = vehicle.get('fuel_type', 'petrol'),
        seats          = int(data.get('seats', 1))
    )
    result = rides.insert_one(new_ride)

    # Pre-calculate fare for display
    dist = haversine(
        float(data['origin_lat']), float(data['origin_lon']),
        COLLEGE_LAT, COLLEGE_LON
    )
    fare = calculate_fare(dist, vehicle['mileage_kmpl'],
                          vehicle.get('fuel_type', 'petrol'))

    return jsonify({
        'message': 'Ride posted successfully',
        'ride_id': str(result.inserted_id),
        'estimated_fare': fare
    }), 201


# ── FIND NEARBY RIDES (passenger searches) ────
@rides_bp.route('/find', methods=['GET'])
@token_required
def find_rides(current_user):
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    if not lat or not lon:
        return jsonify({'error': 'lat and lon query params required'}), 400

    # Get all open rides
    all_rides = list(rides.find({'status': 'open', 'seats_left': {'$gt': 0}}))

    # Run DAA nearby filter
    nearby = find_nearby_rides(lat, lon, all_rides, max_km=2.0)

    # Attach rider info and fare estimate to each ride
    result = []
    for ride in nearby:
        rider = users.find_one({'_id': ride['rider_id']},
                               {'password': 0, 'otp': 0})
        dist = haversine(lat, lon,
                         ride['origin']['lat'], ride['origin']['lon'])
        # Total route: passenger pickup -> college
        route_dist = dist + haversine(
            ride['origin']['lat'], ride['origin']['lon'],
            COLLEGE_LAT, COLLEGE_LON
        )
        fare = calculate_fare(route_dist, ride['mileage_kmpl'], ride['fuel_type'])

        result.append({
            'ride_id':         str(ride['_id']),
            'origin':          ride['origin'],
            'departure_time':  ride['departure_time'],
            'seats_left':      ride['seats_left'],
            'vehicle_name':    ride['vehicle_name'],
            'distance_from_you': ride['distance_from_you'],
            'fare':            fare,
            'rider': {
                'id':          str(rider['_id']),
                'name':        rider['name'],
                'rating':      rider.get('rating', 5.0),
                'trust_score': rider.get('trust_score', 50),
                'verified':    rider['verification']['is_verified'],
                'year':        rider.get('year', ''),
                'branch':      rider.get('branch', '')
            }
        })

    return jsonify({'rides': result, 'count': len(result)})


# ── GET MY POSTED RIDES (rider dashboard) ─────
@rides_bp.route('/my-rides', methods=['GET'])
@token_required
def my_rides(current_user):
    my = list(rides.find({'rider_id': current_user['_id']}))
    return jsonify({'rides': [serialize_ride(r) for r in my]})


# ── GET SINGLE RIDE DETAILS ───────────────────
@rides_bp.route('/<ride_id>', methods=['GET'])
@token_required
def get_ride(current_user, ride_id):
    ride = rides.find_one({'_id': ObjectId(ride_id)})
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    return jsonify(serialize_ride(ride))


# ── CANCEL A RIDE ─────────────────────────────
@rides_bp.route('/<ride_id>/cancel', methods=['PATCH'])
@token_required
def cancel_ride(current_user, ride_id):
    ride = rides.find_one({'_id': ObjectId(ride_id)})
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    if str(ride['rider_id']) != str(current_user['_id']):
        return jsonify({'error': 'Not your ride'}), 403

    rides.update_one({'_id': ObjectId(ride_id)},
                     {'$set': {'status': 'cancelled'}})
    return jsonify({'message': 'Ride cancelled'})