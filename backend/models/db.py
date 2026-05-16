from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/campuspool'))
db     = client['campuspool']

users    = db['users']
rides    = db['rides']
requests = db['requests']

# Indexes for faster queries
users.create_index('email',      unique=True)
rides.create_index('rider_id')
rides.create_index([('origin.lat', 1), ('origin.lon', 1)])
requests.create_index('ride_id')
requests.create_index('passenger_id')
