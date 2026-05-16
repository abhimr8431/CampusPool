from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from models.db import users
from middleware.auth import token_required
from ai.ocr_verify import verify_id_card
from ai.face_match import match_faces

verify_bp = Blueprint('verify', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def upload_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)


# ── STEP 1: UPLOAD ID CARD + OCR ──────────────
@verify_bp.route('/upload-id', methods=['POST'])
@token_required
def upload_id(current_user):
    if 'idCard' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['idCard']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use JPG or PNG'}), 400

    uid      = str(current_user['_id'])
    filename = secure_filename(f'id_{uid}.jpg')
    path     = upload_path(filename)
    file.save(path)

    # Run OCR on the saved image
    ocr_result = verify_id_card(path)

    if ocr_result['passed']:
        users.update_one(
            {'_id': current_user['_id']},
            {'$set': {
                'verification.id_uploaded': True,
                'roll_number': ocr_result.get('roll_number') or current_user.get('roll_number', '')
            }}
        )

    return jsonify({
        'passed':        ocr_result['passed'],
        'message':       ocr_result['message'],
        'college_found': ocr_result.get('college_found'),
        'roll_number':   ocr_result.get('roll_number')
    })


# ── STEP 2: UPLOAD SELFIE + FACE MATCH ────────
@verify_bp.route('/face-match', methods=['POST'])
@token_required
def face_match(current_user):
    if 'selfie' not in request.files:
        return jsonify({'error': 'No selfie uploaded'}), 400

    file = request.files['selfie']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    uid          = str(current_user['_id'])
    id_path      = upload_path(f'id_{uid}.jpg')
    selfie_path  = upload_path(f'selfie_{uid}.jpg')

    if not os.path.exists(id_path):
        return jsonify({'error': 'Please upload your ID card first (Step 1)'}), 400

    file.save(selfie_path)

    result = match_faces(id_path, selfie_path)

    if result['matched']:
        users.update_one(
            {'_id': current_user['_id']},
            {'$set': {
                'verification.selfie_uploaded': True,
                'verification.face_matched':    True
            }}
        )
        _check_and_finalize(current_user['_id'])

    return jsonify({
        'matched':    result['matched'],
        'confidence': result.get('confidence', 0),
        'message':    result['message']
    })


# ── STEP 3: VERIFY EMAIL OTP ──────────────────
# (OTP send/verify is in auth.py — after OTP verified,
#  this endpoint finalizes the trust score)
@verify_bp.route('/finalize', methods=['POST'])
@token_required
def finalize(current_user):
    _check_and_finalize(current_user['_id'])
    user = users.find_one({'_id': current_user['_id']})
    return jsonify({
        'is_verified': user['verification']['is_verified'],
        'trust_score': user.get('trust_score', 50)
    })


# ── GET VERIFICATION STATUS ───────────────────
@verify_bp.route('/status', methods=['GET'])
@token_required
def status(current_user):
    v = current_user.get('verification', {})
    return jsonify({
        'email_verified':  v.get('email_verified', False),
        'id_uploaded':     v.get('id_uploaded', False),
        'face_matched':    v.get('face_matched', False),
        'is_verified':     v.get('is_verified', False),
        'trust_score':     current_user.get('trust_score', 50)
    })


# ── INTERNAL: calculate trust score ───────────
def _check_and_finalize(user_id):
    user = users.find_one({'_id': user_id})
    v    = user.get('verification', {})

    score = 50   # base score
    if v.get('email_verified'):  score += 20
    if v.get('id_uploaded'):     score += 15
    if v.get('face_matched'):    score += 15

    all_verified = (v.get('email_verified') and
                    v.get('id_uploaded')    and
                    v.get('face_matched'))

    users.update_one(
        {'_id': user_id},
        {'$set': {
            'trust_score':                score,
            'verification.is_verified':   all_verified
        }}
    )
