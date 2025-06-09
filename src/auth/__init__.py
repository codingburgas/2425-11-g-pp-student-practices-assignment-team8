from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')
from . import routes

# Import and create the API blueprint
from .api import auth_api_bp
