from app import db

class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_preferences = db.Column(db.JSON, default=lambda: {
        'email': True,
        'web': True,
        'bot_status': True,
        'broadcast_status': True,
        'security_alerts': True
    })
    theme = db.Column(db.String(20), default='light')
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    dashboard_layout = db.Column(db.JSON)

    def to_dict(self):
        return {
            'notification_preferences': self.notification_preferences,
            'theme': self.theme,
            'timezone': self.timezone,
            'language': self.language,
            'dashboard_layout': self.dashboard_layout
        }