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
