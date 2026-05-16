from datetime import datetime, timedelta
from bson import ObjectId

def request_schema(ride_id, passenger_id):
    return {
        'ride_id':      ObjectId(ride_id),
        'passenger_id': ObjectId(passenger_id),
        'status':       'pending',    # pending | accepted | declined | expired
        'expires_at':   datetime.utcnow() + timedelta(minutes=15),
        'created_at':   datetime.utcnow()
    }
