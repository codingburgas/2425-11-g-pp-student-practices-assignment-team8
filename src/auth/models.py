import bcrypt
from flask_login import UserMixin
from .. import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    __password = db.Column("password", db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')
    email_confirmed = db.Column(db.Boolean, default=False)  # ✅ Added for verification

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.__password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))

    @property
    def is_active(self):
        return self.email_confirmed

    @is_active.setter
    def is_active(self, value):
        self.email_confirmed = value


class TrainingResults(db.Model):
    __tablename__ = 'training_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    weights = db.Column(db.Text, nullable=False)  # Using Text for potentially large weight strings
    accuracy = db.Column(db.Float)  # Model accuracy if applicable
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    parameters = db.Column(db.Text)  # Store any additional model parameters as JSON
