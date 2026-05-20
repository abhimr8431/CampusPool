import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()


from routes.auth import auth_bp
from routes.rides    import rides_bp
from routes.requests import requests_bp
from routes.verify   import verify_bp

app = Flask(__name__)
app.config['SECRET_KEY']    = os.getenv('SECRET_KEY', 'dev_secret')
app.config['UPLOAD_FOLDER'] = 'uploads/'
CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*"])
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth_bp,     url_prefix='/api/auth')
app.register_blueprint(rides_bp,    url_prefix='/api/rides')
app.register_blueprint(requests_bp, url_prefix='/api/requests')
app.register_blueprint(verify_bp,   url_prefix='/api/verify')

@app.route('/')
def home():
    return "CampusPool Backend Running 🚀"

@socketio.on('connect')
def on_connect():
    print('Client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    socketio.run(app, debug=True, port=5000)


