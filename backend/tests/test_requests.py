import os
import jwt
import pytest
from bson import ObjectId

# Enable mongomock before importing app and db
os.environ['USE_MONGO_MOCK'] = '1'
from app import app as flask_app
from models.db import users, rides, requests as req_col
from models.user import user_schema
from models.ride import ride_schema

SECRET = os.getenv('SECRET_KEY', 'dev_secret')

@pytest.fixture
def client():
    return flask_app.test_client()

def make_token(user_id: ObjectId):
    token = jwt.encode({'user_id': str(user_id)}, SECRET, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def test_send_and_accept_request_flow(client):
    # Create rider user with vehicle mileage
    rider_doc = user_schema(
        name='Rider',
        email='rider@rvce.edu.in',
        password_hash='hashed',
        college='RVCE',
        year='3',
        branch='CSE',
        phone='9999999999',
        vehicle={'name': 'Car', 'fuel_type': 'petrol', 'mileage_kmpl': 20, 'reg_number': 'KA01'},
    )
    rider_res = users.insert_one(rider_doc)
    rider_id = rider_res.inserted_id

    # Create passenger user
    passenger_doc = user_schema(
        name='Passenger',
        email='pass@rvce.edu.in',
        password_hash='hashed',
        college='RVCE',
        year='2',
        branch='ISE',
        phone='8888888888'
    )
    passenger_res = users.insert_one(passenger_doc)
    passenger_id = passenger_res.inserted_id

    rider_token = make_token(rider_id)
    passenger_token = make_token(passenger_id)

    # Rider posts a ride
    post_payload = {
        'origin_lat': 12.92,
        'origin_lon': 77.49,
        'origin_name': 'Magadi Road',
        'departure_time': '2026-05-22T08:00:00Z',
        'seats': 2
    }
    rv = client.post('/api/rides/post', json=post_payload, headers={'Authorization': f'Bearer {rider_token}'})
    assert rv.status_code == 201
    data = rv.get_json()
    ride_id = data['ride_id']

    # Passenger sends request
    rv2 = client.post('/api/requests/send', json={'ride_id': ride_id, 'passenger_lat': 12.921, 'passenger_lon': 77.495}, headers={'Authorization': f'Bearer {passenger_token}'})
    assert rv2.status_code == 201
    data2 = rv2.get_json()
    req_id = data2['request_id']

    # Rider accepts request
    rv3 = client.patch(f'/api/requests/{req_id}/accept', headers={'Authorization': f'Bearer {rider_token}'})
    assert rv3.status_code == 200
    data3 = rv3.get_json()
    assert 'message' in data3

    # Verify seats_left decremented
    ride_doc = rides.find_one({'_id': ObjectId(ride_id)})
    assert ride_doc['seats_left'] == 1

    # Verify request status updated
    req_doc = req_col.find_one({'_id': ObjectId(req_id)})
    assert req_doc['status'] == 'accepted'
*** End Patch