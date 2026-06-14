from datetime import datetime, timedelta
from bson import ObjectId
from models.db import rides, requests as req_col


class RequestAcceptError(Exception):
    pass

def request_schema(ride_id, passenger_id):
    return {
        'ride_id':      ObjectId(ride_id),
        'passenger_id': ObjectId(passenger_id),
        'status':       'pending',    # pending | accepted | declined | expired
        'expires_at':   datetime.utcnow() + timedelta(minutes=15),
        'created_at':   datetime.utcnow()
    }


def accept_request(req_id, rider_id):
    """
    Programmatically accept a passenger request.
    Returns the updated request document on success.
    Raises RequestAcceptError on failure.
    """
    req = req_col.find_one({'_id': ObjectId(req_id)})
    if not req:
        raise RequestAcceptError('Request not found')

    ride = rides.find_one({'_id': req['ride_id']})
    if not ride:
        raise RequestAcceptError('Ride not found')
    if str(ride['rider_id']) != str(rider_id):
        raise RequestAcceptError('Not your ride')
    if req['status'] != 'pending':
        raise RequestAcceptError(f'Request is already {req["status"]}')
    if datetime.utcnow() > req['expires_at']:
        req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'expired'}})
        raise RequestAcceptError('Request has expired')

    # Attempt atomic seat decrement
    req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'accepted'}})
    update_result = rides.update_one({'_id': req['ride_id'], 'seats_left': {'$gt': 0}},
                                     {'$inc': {'seats_left': -1}, '$push': {'passengers': req['passenger_id']}})
    if update_result.modified_count == 0:
        # revert
        req_col.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 'declined'}})
        raise RequestAcceptError('Failed to accept request — ride may be full')

    # Mark ride full if needed
    updated_ride = rides.find_one({'_id': req['ride_id']})
    if updated_ride and updated_ride.get('seats_left', 0) == 0:
        rides.update_one({'_id': req['ride_id']}, {'$set': {'status': 'full'}})

    return req_col.find_one({'_id': ObjectId(req_id)})
