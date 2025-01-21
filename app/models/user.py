from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(20), nullable=False, default='user')

    # Relationships
    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    advertisements = db.relationship('Advertisement', backref='owner', lazy='dynamic')

    def __init__(self, username, password, role='user'):
        self.public_id = str(uuid.uuid4())
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }