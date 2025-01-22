from flask import jsonify, request, current_app
from app.api import bp
from app.api.auth import token_required
from app.models.user import User
from app import db
from datetime import datetime

@bp.route('/users/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user profile"""
    return jsonify(current_user.to_dict())

@bp.route('/users/me', methods=['PUT'])
@token_required
def update_current_user(current_user):
    """Update current user profile"""
    data = request.get_json()
    
    if 'username' in data and data['username'] != current_user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        current_user.username = data['username']

    if 'old_password' in data and 'new_password' in data:
        if not current_user.check_password(data['old_password']):
            return jsonify({'message': 'Current password is incorrect'}), 400
        current_user.set_password(data['new_password'])

    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f'Error updating user: {str(e)}')
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile'}), 500

@bp.route('/users/me/api-keys', methods=['GET'])
@token_required
def get_api_keys(current_user):
    """Get user's API keys"""
    return jsonify(current_user.get_api_keys())

@bp.route('/users/me/api-keys', methods=['POST'])
@token_required
def create_api_key(current_user):
    """Create new API key"""
    data = request.get_json()
    name = data.get('name', 'API Key')
    
    try:
        key = current_user.create_api_key(name)
        return jsonify({
            'message': 'API key created successfully',
            'key': key
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error creating API key: {str(e)}')
        return jsonify({'message': 'Failed to create API key'}), 500

@bp.route('/users/me/api-keys/<key_id>', methods=['DELETE'])
@token_required
def delete_api_key(current_user, key_id):
    """Delete API key"""
    try:
        current_user.delete_api_key(key_id)
        return jsonify({'message': 'API key deleted successfully'})
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f'Error deleting API key: {str(e)}')
        return jsonify({'message': 'Failed to delete API key'}), 500

@bp.route('/users/me/activity', methods=['GET'])
@token_required
def get_activity_log(current_user):
    """Get user activity log"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        activities = current_user.get_activity_log(page, per_page)
        return jsonify(activities)
    except Exception as e:
        current_app.logger.error(f'Error getting activity log: {str(e)}')
        return jsonify({'message': 'Failed to get activity log'}), 500

@bp.route('/users/me/settings', methods=['GET'])
@token_required
def get_user_settings(current_user):
    """Get user settings"""
    return jsonify(current_user.get_settings())

@bp.route('/users/me/settings', methods=['PUT'])
@token_required
def update_user_settings(current_user):
    """Update user settings"""
    data = request.get_json()
    
    try:
        current_user.update_settings(data)
        db.session.commit()
        return jsonify({
            'message': 'Settings updated successfully',
            'settings': current_user.get_settings()
        })
    except Exception as e:
        current_app.logger.error(f'Error updating settings: {str(e)}')
        db.session.rollback()
        return jsonify({'message': 'Failed to update settings'}), 500

# Admin routes
@bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')

        query = User.query
        if search:
            query = query.filter(User.username.ilike(f'%{search}%'))

        pagination = query.paginate(page=page, per_page=per_page)
        users = pagination.items

        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        current_app.logger.error(f'Error getting users: {str(e)}')
        return jsonify({'message': 'Failed to get users'}), 500

@bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """Update user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    
    try:
        if 'role' in data:
            user.role = data['role']
        if 'status' in data:
            user.status = data['status']
        
        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f'Error updating user: {str(e)}')
        db.session.rollback()
        return jsonify({'message': 'Failed to update user'}), 500

@bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """Delete user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    if str(current_user.id) == user_id:
        return jsonify({'message': 'Cannot delete yourself'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        current_app.logger.error(f'Error deleting user: {str(e)}')
        db.session.rollback()
        return jsonify({'message': 'Failed to delete user'}), 500