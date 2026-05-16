from datetime import datetime
from bson import ObjectId

def ride_schema(
    rider_id, origin_lat, origin_lon, origin_name,
    college_lat, college_lon, college_name,
    departure_time, vehicle_name, mileage_kmpl,
    fuel_type='petrol', seats=1
):
    return {
        'rider_id':       ObjectId(rider_id),
        'origin': {
            'lat':  origin_lat,
            'lon':  origin_lon,
            'name': origin_name
        },
        'destination': {
            'lat':  college_lat,
            'lon':  college_lon,
            'name': college_name
        },
        'departure_time': departure_time,
        'vehicle_name':   vehicle_name,
        'mileage_kmpl':   mileage_kmpl,
        'fuel_type':      fuel_type,
        'seats_total':    seats,
        'seats_left':     seats,
        'status':         'open',        # open | full | completed | cancelled
        'passengers':     [],
        'created_at':     datetime.utcnow()
    }