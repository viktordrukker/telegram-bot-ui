from flask import jsonify, request
from app.api import bp
from app.models.user import User
from app import db
import jwt
import datetime
from functools import wraps
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields!'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 400

    new_user = User(
        username=data['username'],
        password=data['password'],
        role=data.get('role', 'user')
    )
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

@bp.route('/auth/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify!'}), 401

    user = User.query.filter_by(username=auth['username']).first()

    if not user:
        return jsonify({'message': 'User not found!'}), 404

    if user.check_password(auth['password']):
        token = jwt.encode(
            {
                'public_id': user.public_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            current_app.config['SECRET_KEY']
        )
        return jsonify({
            'token': token,
            'user': user.to_dict()
        })

    return jsonify({'message': 'Invalid credentials!'}), 401

@bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify(current_user.to_dict())