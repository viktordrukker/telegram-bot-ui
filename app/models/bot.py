from app import db
from datetime import datetime
from enum import Enum
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import InvalidStateError  # Ensure this exception exists

class BotStatus(str, Enum):
    STOPPED = 'stopped'
    RUNNING = 'running'
    ERROR = 'error'
    MAINTENANCE = 'maintenance'

class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bot_token = db.Column(db.String(100), unique=True, nullable=False)
    bot_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(BotStatus), nullable=False, default=BotStatus.STOPPED)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    instance_id = db.Column(db.String(50))
    version = db.Column(db.String(20), default='1.0.0')
    config = db.Column(db.JSON, default=lambda: {'max_connections': 5})

    # Relationships
    messages = db.relationship('Message', back_populates='bot', lazy='selectin')
    analytics = db.relationship('Analytics', back_populates='bot', lazy='selectin')
    logs = db.relationship('Log', back_populates='bot', lazy='selectin')

    def to_dict(self):
        return {
            'id': self.id,
            'bot_name': self.bot_name,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'version': self.version,
            'instance_id': self.instance_id,
            'config': self.config
        }

    def start(self):
        """Transition to running state with validation"""
        if self.status == BotStatus.RUNNING:
            raise InvalidStateError('Bot already running')
            
        self.status = BotStatus.RUNNING
        self.last_active = datetime.utcnow()

    def stop(self):
        """Graceful shutdown procedure"""
        if self.status == BotStatus.STOPPED:
            raise InvalidStateError('Bot already stopped')
            
        self.status = BotStatus.STOPPED

    def update_config(self, new_config: dict):
        """Safely merge configuration changes"""
        self.config = {**self.config, **new_config}

    def validate_token(self):
        """Basic token format validation"""
        if not self.bot_token.startswith('bot_'):
            raise ValueError('Invalid bot token format')
        if len(self.bot_token) < 20:
            raise ValueError('Token too short')