from app import db
from datetime import datetime

class Analytics(db.Model):
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)
    metric_value = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'timestamp': self.timestamp.isoformat()
        }