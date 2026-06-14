from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from models.db import users, rides
from models.user import user_schema
from models.ride import ride_schema

load_dotenv()

bcrypt = Bcrypt()

TEST_USER = {
    'name': 'CampusPool Tester',
    'email': 'testuser@rvce.edu.in',
    'password': 'TestPass123!',
    'college': 'Ramaiah Institute of Technology',
    'year': '3rd',
    'branch': 'CSE',
    'phone': '9999999999',
    'roll_number': '1RV20CS001',
    'vehicle': {
        'name': 'Honda City',
        'fuel_type': 'petrol',
        'mileage_kmpl': 18,
        'reg_number': 'KA01AB1234'
    },
    'emergency_contact': {
        'name': 'Test Guardian',
        'phone': '8888888888'
    },
    'verification': {
        'email_verified': True,
        'id_uploaded': True,
        'selfie_uploaded': True,
        'face_matched': True,
        'is_verified': True
    },
    'trust_score': 92,
    'rating': 4.9,
    'total_rides': 14
}

DEMO_RIDES = [
    {
        'origin_lat': 12.9352,
        'origin_lon': 77.6245,
        'origin_name': 'Kengeri',
        'departure_time': '08:12',
        'seats': 2
    },
    {
        'origin_lat': 12.9440,
        'origin_lon': 77.6200,
        'origin_name': 'Banashankari',
        'departure_time': '08:40',
        'seats': 3
    },
    {
        'origin_lat': 12.9370,
        'origin_lon': 77.6210,
        'origin_name': 'Sultanpalya',
        'departure_time': '08:25',
        'seats': 2
    }
]

existing = users.find_one({'email': TEST_USER['email']})
if existing:
    print(f"User already exists: {TEST_USER['email']} (id={existing['_id']})")
    existing_user = existing
else:
    password_hash = bcrypt.generate_password_hash(TEST_USER['password']).decode('utf-8')
    new_user = user_schema(
        name=TEST_USER['name'],
        email=TEST_USER['email'],
        password_hash=password_hash,
        roll_number=TEST_USER['roll_number'],
        college=TEST_USER['college'],
        year=TEST_USER['year'],
        branch=TEST_USER['branch'],
        phone=TEST_USER['phone'],
        vehicle=TEST_USER['vehicle'],
        emergency_contact=TEST_USER['emergency_contact']
    )
    new_user['verification'] = TEST_USER['verification']
    new_user['trust_score'] = TEST_USER['trust_score']
    new_user['rating'] = TEST_USER['rating']
    new_user['total_rides'] = TEST_USER['total_rides']
    result = users.insert_one(new_user)
    existing_user = users.find_one({'_id': result.inserted_id})
    print(f"Inserted test user: {TEST_USER['email']} (id={result.inserted_id})")

if existing_user:
    for demo in DEMO_RIDES:
        query = {
            'rider_id': existing_user['_id'],
            'origin.name': demo['origin_name'],
            'departure_time': demo['departure_time']
        }
        if not rides.find_one(query):
            print(f"Creating demo ride: {demo['origin_name']} at {demo['departure_time']}")
            demo_ride = ride_schema(
                rider_id=str(existing_user['_id']),
                origin_lat=demo['origin_lat'],
                origin_lon=demo['origin_lon'],
                origin_name=demo['origin_name'],
                college_lat=13.0128,
                college_lon=77.5748,
                college_name='Ramaiah Institute of Technology',
                departure_time=demo['departure_time'],
                vehicle_name=TEST_USER['vehicle']['name'],
                mileage_kmpl=TEST_USER['vehicle']['mileage_kmpl'],
                fuel_type=TEST_USER['vehicle']['fuel_type'],
                seats=demo['seats']
            )
            rides.insert_one(demo_ride)

print('Login credentials:')
print(f"  email: {TEST_USER['email']}")
print(f"  password: {TEST_USER['password']}")

# --- Add a second demo login/user ---
SECOND_USER = {
    'name': 'CampusPool Demo Rider',
    'email': 'demorider@rvce.edu.in',
    'password': 'DemoPass123!',
    'college': 'Ramaiah Institute of Technology',
    'year': '4th',
    'branch': 'ISE',
    'phone': '7777777777',
    'roll_number': '1RV19IS002',
    'vehicle': {
        'name': 'Suzuki Swift',
        'fuel_type': 'petrol',
        'mileage_kmpl': 22,
        'reg_number': 'KA02CD5678'
    },
    'emergency_contact': {
        'name': 'Demo Guardian',
        'phone': '6666666666'
    },
    'verification': {
        'email_verified': True,
        'id_uploaded': True,
        'selfie_uploaded': True,
        'face_matched': True,
        'is_verified': True
    },
    'trust_score': 85,
    'rating': 4.7,
    'total_rides': 8
}

SECOND_DEMO_RIDES = [
    {
        'origin_lat': 12.9300,
        'origin_lon': 77.6100,
        'origin_name': 'Jayanagar',
        'departure_time': '08:05',
        'seats': 2
    },
    {
        'origin_lat': 12.9400,
        'origin_lon': 77.6150,
        'origin_name': 'Basavanagudi',
        'departure_time': '08:30',
        'seats': 1
    }
]

existing2 = users.find_one({'email': SECOND_USER['email']})
if existing2:
    print(f"User already exists: {SECOND_USER['email']} (id={existing2['_id']})")
    existing_user2 = existing2
else:
    password_hash = bcrypt.generate_password_hash(SECOND_USER['password']).decode('utf-8')
    new_user2 = user_schema(
        name=SECOND_USER['name'],
        email=SECOND_USER['email'],
        password_hash=password_hash,
        roll_number=SECOND_USER['roll_number'],
        college=SECOND_USER['college'],
        year=SECOND_USER['year'],
        branch=SECOND_USER['branch'],
        phone=SECOND_USER['phone'],
        vehicle=SECOND_USER['vehicle'],
        emergency_contact=SECOND_USER['emergency_contact']
    )
    new_user2['verification'] = SECOND_USER['verification']
    new_user2['trust_score'] = SECOND_USER['trust_score']
    new_user2['rating'] = SECOND_USER['rating']
    new_user2['total_rides'] = SECOND_USER['total_rides']
    result2 = users.insert_one(new_user2)
    existing_user2 = users.find_one({'_id': result2.inserted_id})
    print(f"Inserted demo user: {SECOND_USER['email']} (id={result2.inserted_id})")

if existing_user2:
    for demo in SECOND_DEMO_RIDES:
        query = {
            'rider_id': existing_user2['_id'],
            'origin.name': demo['origin_name'],
            'departure_time': demo['departure_time']
        }
        if not rides.find_one(query):
            print(f"Creating demo ride for second user: {demo['origin_name']} at {demo['departure_time']}")
            demo_ride = ride_schema(
                rider_id=str(existing_user2['_id']),
                origin_lat=demo['origin_lat'],
                origin_lon=demo['origin_lon'],
                origin_name=demo['origin_name'],
                college_lat=13.0128,
                college_lon=77.5748,
                college_name='Ramaiah Institute of Technology',
                departure_time=demo['departure_time'],
                vehicle_name=SECOND_USER['vehicle']['name'],
                mileage_kmpl=SECOND_USER['vehicle']['mileage_kmpl'],
                fuel_type=SECOND_USER['vehicle']['fuel_type'],
                seats=demo['seats']
            )
            rides.insert_one(demo_ride)

print('Additional login credentials:')
print(f"  email: {SECOND_USER['email']}")
print(f"  password: {SECOND_USER['password']}")
