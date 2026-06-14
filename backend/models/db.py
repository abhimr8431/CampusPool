from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Support an in-memory mongomock client when running tests by setting
# the environment variable `USE_MONGO_MOCK=1`. This keeps production
# behavior unchanged while making tests fast and hermetic.
use_mongo_mock = os.getenv('USE_MONGO_MOCK', '0') == '1'
if use_mongo_mock:
	try:
		import mongomock
	except Exception:
		raise RuntimeError('mongomock required for USE_MONGO_MOCK=1')
	client = mongomock.MongoClient()
else:
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
