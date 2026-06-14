import sys
import os
# Ensure project root is on path when running this script directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.db import users, rides, requests as req_col
from models.user import user_schema
from models.ride import ride_schema
from models.request import request_schema, accept_request
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# create rider
r = user_schema('Rider2','r2@rvce.edu.in','pw',college='RVCE',year='3',branch='CSE',phone='999')
res = users.insert_one(r)
rider_id = res.inserted_id

# create passenger
p = user_schema('P','p@rvce.edu.in','pw',college='RVCE',year='2',branch='ISE',phone='888')
pres = users.insert_one(p)
pass_id = pres.inserted_id

# create ride
ride = ride_schema(str(rider_id),12.92,77.62,'Loc',12.9237,77.4988,'RVCE','08:00','Car',20,'petrol',2)
ride_res = rides.insert_one(ride)
ride_id = ride_res.inserted_id

# create request
req = request_schema(str(ride_id), str(pass_id))
req_res = req_col.insert_one(req)
req_id = req_res.inserted_id

print('Before accept seats_left:', rides.find_one({'_id': ride_id})['seats_left'])
# accept programmatically
try:
    updated = accept_request(str(req_id), rider_id)
    print('Accepted request:', updated)
    print('After accept seats_left:', rides.find_one({'_id': ride_id})['seats_left'])
except Exception as e:
    print('Accept failed:', e)
