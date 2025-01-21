from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bot_admin:wewffikp@172.31.127.182:5432/telegram_bot_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(
        public_id=str(uuid.uuid4()),
        username=data['username'],
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        return jsonify({'message': 'Could not verify!'}), 401

    user = User.query.filter_by(username=auth['username']).first()

    if not user:
        return jsonify({'message': 'User not found!'}), 404

    if check_password_hash(user.password_hash, auth['password']):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
            app.config['SECRET_KEY']
        )
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()

    if not data or not data['old_password'] or not data['new_password']:
        return jsonify({'message': 'Invalid request!'}), 400

    if not check_password_hash(current_user.password_hash, data['old_password']):
        return jsonify({'message': 'Old password is incorrect!'}), 401

    current_user.password_hash = generate_password_hash(data['new_password'], method='sha256')
    db.session.commit()

    return jsonify({'message': 'Password changed successfully!'}), 200

@app.route('/bots/<int:bot_id>/start', methods=['POST'])
@token_required
def start_bot(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found or unauthorized!'}), 404

    try:
        # Start the bot using supervisord
        subprocess.run(['sudo', 'supervisorctl', 'start', f'bot_{bot_id}'])
        bot.status = 'running'
        db.session.commit()
    except Exception as e:
        return jsonify({'message': f'Failed to start bot: {str(e)}'}), 500

    return jsonify({'message': f'Bot {bot_id} started successfully!'}), 200

@app.route('/bots/<int:bot_id>/stop', methods=['POST'])
@token_required
def stop_bot(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found or unauthorized!'}), 404

    try:
        # Stop the bot using supervisord
        subprocess.run(['sudo', 'supervisorctl', 'stop', f'bot_{bot_id}'])
        bot.status = 'stopped'
        db.session.commit()
    except Exception as e:
        return jsonify({'message': f'Failed to stop bot: {str(e)}'}), 500

    return jsonify({'message': f'Bot {bot_id} stopped successfully!'}), 200

@app.route('/bots/<int:bot_id>/restart', methods=['POST'])
@token_required
def restart_bot(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found or unauthorized!'}), 404

    try:
        # Restart the bot using supervisord
        subprocess.run(['sudo', 'supervisorctl', 'restart', f'bot_{bot_id}'])
        bot.status = 'running'
        db.session.commit()
    except Exception as e:
        return jsonify({'message': f'Failed to restart bot: {str(e)}'}), 500

    return jsonify({'message': f'Bot {bot_id} restarted successfully!'}), 200

@app.route('/bots/<int:bot_id>/status', methods=['GET'])
@token_required
def get_bot_status(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found or unauthorized!'}), 404

    return jsonify({'status': bot.status}), 200

@app.route('/')
def index():
    return render_template('index.html')

import os
import subprocess

@app.route('/add_bot', methods=['POST'])
@token_required
def add_bot(current_user):
    data = request.get_json()
    bot_token = data.get('bot_token')
    bot_name = data.get('bot_name')

    if not bot_token or not bot_name:
        return jsonify({'message': 'Bot token and name are required!'}), 400

    # Save bot details to the database
    new_bot = Bot(
        user_id=current_user.id,
        bot_token=bot_token,
        status='stopped'
    )
    db.session.add(new_bot)
    db.session.commit()

    # Create supervisord configuration file
    bot_id = new_bot.id
    config_content = f"""
    [program:bot_{bot_id}]
    command=python3 /path/to/bot_script.py --token {bot_token}
    directory=/path/to/bot_directory
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/bot_{bot_id}.err.log
    stdout_logfile=/var/log/bot_{bot_id}.out.log
    """
    config_path = f"/etc/supervisor/conf.d/bot_{bot_id}.conf"

    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Reload supervisord
        subprocess.run(['sudo', 'supervisorctl', 'reread'])
        subprocess.run(['sudo', 'supervisorctl', 'update'])
    except Exception as e:
        return jsonify({'message': f'Failed to configure supervisord: {str(e)}'}), 500

    return jsonify({'message': f'Bot {bot_name} added successfully!', 'bot_id': bot_id}), 201

if __name__ == '__main__':
    app.run(port=56497, debug=True)