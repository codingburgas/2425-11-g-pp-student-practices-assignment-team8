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


club_members = db.Table('club_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('clubs.id'), primary_key=True)
)

class EventDetail(db.Model):
    __tablename__ = 'event_details'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), default="This is a scheduled club event. Details will be updated by the teacher.")
    location = db.Column(db.String(100), default="Room 101")
    start_time = db.Column(db.Time, default=datetime.strptime("15:00:00", "%H:%M:%S").time())
    end_time = db.Column(db.Time, default=datetime.strptime("16:00:00", "%H:%M:%S").time())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ClubEvent(db.Model):
    __tablename__ = 'club_events'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    detail_id = db.Column(db.Integer, db.ForeignKey('event_details.id'), nullable=True)

    detail = db.relationship('EventDetail', backref='club_event', uselist=False)


