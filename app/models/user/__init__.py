from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import secrets
from . import (
    UserApiKey,
    UserActivity,
    UserSettings
)

# Moved to dedicated modules under models/user/
# - api_key.py
# - activity.py 
# - settings.py

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(20), nullable=False, default='user')
    status = db.Column(db.String(20), nullable=False, default='active')
    last_login = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime)

    # Relationships
    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    advertisements = db.relationship('Advertisement', backref='owner', lazy='dynamic')
    api_keys = db.relationship('UserApiKey', backref='user', lazy='dynamic',
                             cascade='all, delete-orphan')
    activities = db.relationship('UserActivity', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False,
                             cascade='all, delete-orphan')

    def __init__(self, username, password, email=None, role='user'):
        self.public_id = str(uuid.uuid4())
        self.username = username
        self.set_password(password)
        self.email = email
        self.role = role
        self.settings = UserSettings()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def create_api_key(self, name, expires_in=None):
        """Create a new API key"""
        key = secrets.token_urlsafe(32)
        key_hash = generate_password_hash(key)
        
        api_key = UserApiKey(
            user_id=self.id,
            key_hash=key_hash,
            name=name,
            expires_at=(datetime.utcnow() + timedelta(days=expires_in)) if expires_in else None
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        return {
            'key': key,
            'key_id': api_key.id,
            'name': api_key.name,
            'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None
        }

    def delete_api_key(self, key_id):
        """Delete an API key"""
        api_key = UserApiKey.query.filter_by(id=key_id, user_id=self.id).first()
        if not api_key:
            raise ValueError('API key not found')
        
        db.session.delete(api_key)
        db.session.commit()

    def get_api_keys(self):
        """Get all API keys"""
        return [key.to_dict() for key in self.api_keys]

    def log_activity(self, action, details=None, ip_address=None):
        """Log user activity"""
        activity = UserActivity(
            user_id=self.id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.session.add(activity)
        db.session.commit()

    def get_activity_log(self, page=1, per_page=20):
        """Get paginated activity log"""
        pagination = self.activities.order_by(UserActivity.timestamp.desc())\
            .paginate(page=page, per_page=per_page)
        
        return {
            'activities': [activity.to_dict() for activity in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }

    def get_settings(self):
        """Get user settings"""
        if not self.settings:
            self.settings = UserSettings()
            db.session.add(self.settings)
            db.session.commit()
        return self.settings.to_dict()

    def update_settings(self, settings):
        """Update user settings"""
        if not self.settings:
            self.settings = UserSettings()
            db.session.add(self.settings)

        for key, value in settings.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)

    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'public_id': self.public_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'settings': self.get_settings()
        }