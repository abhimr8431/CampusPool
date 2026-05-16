from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.db import users, rides, requests as req_col
from middleware.auth import token_required

profile_bp = Blueprint('profile', __name__)


# ── GET MY PROFILE ────────────────────────────
@profile_bp.route('/me', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'id':          str(current_user['_id']),
        'name':        current_user['name'],
        'email':       current_user['email'],
        'college':     current_user.get('college', ''),
        'year':        current_user.get('year', ''),
        'branch':      current_user.get('branch', ''),
        'phone':       current_user.get('phone', ''),
        'vehicle':     current_user.get('vehicle', {}),
        'trust_score': current_user.get('trust_score', 50),
        'rating':      current_user.get('rating', 5.0),
        'total_rides': current_user.get('total_rides', 0),
        'verification': current_user.get('verification', {}),
        'emergency_contact': current_user.get('emergency_contact', {})
    })


# ── UPDATE PROFILE ────────────────────────────
@profile_bp.route('/update', methods=['PATCH'])
@token_required
def update_profile(current_user):
    data    = request.get_json()
    allowed = ['name', 'phone', 'year', 'branch', 'vehicle', 'emergency_contact']
    update  = {k: v for k, v in data.items() if k in allowed}

    if not update:
        return jsonify({'error': 'Nothing to update'}), 400

    users.update_one({'_id': current_user['_id']}, {'$set': update})
    return jsonify({'message': 'Profile updated'})


# ── RATE A USER AFTER RIDE ────────────────────
@profile_bp.route('/rate', methods=['POST'])
@token_required
def rate_user(current_user):
    data    = request.get_json()
    user_id = data.get('user_id')
    rating  = float(data.get('rating', 5.0))

    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    if not (1.0 <= rating <= 5.0):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    target = users.find_one({'_id': ObjectId(user_id)})
    if not target:
        return jsonify({'error': 'User not found'}), 404

    # Rolling average rating
    current_rating     = target.get('rating', 5.0)
    total_rides        = target.get('total_rides', 1)
    new_rating         = round(
        (current_rating * (total_rides - 1) + rating) / total_rides, 2
    )
    # Update trust score based on rating
    trust_bonus = 5 if rating >= 4.5 else (0 if rating >= 3.5 else -5)

    users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set':  {'rating': new_rating},
         '$inc':  {'trust_score': trust_bonus, 'total_rides': 1}}
    )
    return jsonify({'message': 'Rating submitted', 'new_rating': new_rating})


# ── GET OTHER USER PROFILE (public view) ──────
@profile_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    user = users.find_one({'_id': ObjectId(user_id)},
                          {'password': 0, 'otp': 0, 'otp_expiry': 0})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user['_id'] = str(user['_id'])
    return jsonify(user)
