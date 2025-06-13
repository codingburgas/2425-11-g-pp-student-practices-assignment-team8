from .. import db
from datetime import datetime
class ModelInfo(db.Model):
    __tablename__ = 'model_info'
    id = db.Column(db.Integer, primary_key=True)
    weights = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    modelName = db.Column(db.String, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)  # Added accuracy field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parameters = db.Column(db.String, nullable=True)  # Added parameters field
class ClubRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    club_name = db.Column(db.String(64))
    status = db.Column(db.String(20), default='pending')  # e.g., 'pending', 'accepted', 'declined'


class Club(db.Model):
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    participants = db.Column(db.Integer, default=0)
    users = db.relationship('User', secondary='club_members', back_populates='clubs')


# Association table for many-to-many relationship (optional, if each club has many users and vice versa)
club_members = db.Table('club_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('clubs.id'), primary_key=True)
)

class ClubEvent(db.Model):
    __tablename__ = 'club_events'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    event_date = db.Column(db.Date, nullable=False)

