from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
import os
import smtplib
import random
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models.db import users
from models.user import user_schema
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)
bcrypt  = Bcrypt()

ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', 'rvce.edu.in').split(',')


def send_otp_email(to_email: str, otp: int):
    """Send OTP to college email address."""
    msg            = MIMEMultipart()
    msg['From']    = os.getenv('EMAIL_USER')
    msg['To']      = to_email
    msg['Subject'] = 'CampusPool â€” Email Verification OTP'
    body = f"""
    Hi there!
    
    Your CampusPool verification OTP is: {otp}
    
    This OTP expires in 10 minutes.
    Do not share this with anyone.
    
    â€” CampusPool Team
    """
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f'Email error: {e}')
        return False


# â”€â”€ REGISTER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@auth_bp.route('/register', methods=['POST'])
def register():
    data  = request.get_json()
    email = data.get('email', '').lower().strip()

    # Validate college email domain
    domain = email.split('@')[-1] if '@' in email else ''
    if domain not in ALLOWED_DOMAINS:
        return jsonify({'error': f'Use your college email. Allowed: {", ".join(ALLOWED_DOMAINS)}'}), 400

    # Check duplicate
    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400

    required = ['name', 'email', 'password', 'college', 'year', 'branch', 'phone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    vehicle = data.get('vehicle', {})   # name, fuel_type, mileage_kmpl, reg_number

    new_user = user_schema(
        name          = data['name'],
        email         = email,
        password_hash = password_hash,
        roll_number   = data.get('roll_number', ''),
        college       = data['college'],
        year          = data['year'],
        branch        = data['branch'],
        phone         = data['phone'],
        vehicle       = vehicle,
        emergency_contact = data.get('emergency_contact', {})
    )
    result = users.insert_one(new_user)
    return jsonify({'message': 'Registered successfully',
                    'user_id': str(result.inserted_id)}), 201


# â”€â”€ SEND OTP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data  = request.get_json()
    email = data.get('email', '').lower().strip()
    user  = users.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    otp = random.randint(100000, 999999)
    users.update_one(
        {'email': email},
        {'$set': {
            'otp':        str(otp),
            'otp_expiry': datetime.utcnow() + timedelta(minutes=10)
        }}
    )
    sent = send_otp_email(email, otp)
    if sent:
        return jsonify({'message': 'OTP sent to your college email'})
    # In dev mode â€” return OTP directly (REMOVE IN PRODUCTION)
    return jsonify({'message': 'Email failed (dev mode)', 'otp': otp})


# â”€â”€ VERIFY OTP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data  = request.get_json()
    email = data.get('email', '').lower().strip()
    otp   = str(data.get('otp', ''))
    user  = users.find_one({'email': email})

    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.get('otp') != otp:
        return jsonify({'error': 'Wrong OTP'}), 400
    if datetime.utcnow() > user.get('otp_expiry', datetime.utcnow()):
        return jsonify({'error': 'OTP expired'}), 400

    users.update_one(
        {'email': email},
        {'$set': {'verification.email_verified': True, 'otp': None}}
    )
    return jsonify({'message': 'Email verified successfully'})


# â”€â”€ LOGIN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@auth_bp.route('/login', methods=['POST'])
def login():
    data  = request.get_json()
    email = data.get('email', '').lower().strip()
    user  = users.find_one({'email': email})

    if not user or not bcrypt.check_password_hash(user['password'], data.get('password', '')):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = jwt.encode(
        {
            'user_id': str(user['_id']),
            'exp':     datetime.utcnow() + timedelta(days=7)
        },
        os.getenv('SECRET_KEY'),
        algorithm='HS256'
    )
    return jsonify({
        'token':   token,
        'user': {
            'id':      str(user['_id']),
            'name':    user['name'],
            'email':   user['email'],
            'college': user['college'],
            'verified': user.get('verification', {}).get('is_verified', False)
        }
    })