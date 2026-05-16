from datetime import datetime

def user_schema(
    name, email, password_hash,
    roll_number='', college='', year='', branch='',
    phone='', vehicle=None, emergency_contact=None
):
    return {
        'name':         name,
        'email':        email,
        'password':     password_hash,
        'roll_number':  roll_number,
        'college':      college,
        'year':         year,
        'branch':       branch,
        'phone':        phone,
        'vehicle': vehicle or {
            'name':         '',
            'fuel_type':    'petrol',
            'mileage_kmpl': 0,
            'reg_number':   ''
        },
        'verification': {
            'email_verified':  False,
            'id_uploaded':     False,
            'selfie_uploaded': False,
            'face_matched':    False,
            'is_verified':     False
        },
        'otp':               None,
        'otp_expiry':        None,
        'trust_score':       50,
        'rating':            5.0,
        'total_rides':       0,
        'emergency_contact': emergency_contact or {'name': '', 'phone': ''},
        'created_at':        datetime.utcnow()
    }