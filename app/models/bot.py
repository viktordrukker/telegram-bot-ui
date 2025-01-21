from app import db
from datetime import datetime

class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bot_token = db.Column(db.String(100), unique=True, nullable=False)
    bot_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='stopped')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_active = db.Column(db.DateTime)
    instance_id = db.Column(db.String(50))

    # Relationships
    messages = db.relationship('Message', backref='bot', lazy='dynamic')
    analytics = db.relationship('Analytics', backref='bot', lazy='dynamic')
    logs = db.relationship('Log', backref='bot', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'bot_name': self.bot_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

    def update_status(self, status):
        self.status = status
        if status == 'running':
            self.last_active = datetime.utcnow()
        db.session.commit()