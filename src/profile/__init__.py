from flask import Blueprint

prof_bp = Blueprint('profile', __name__, url_prefix='/profile', template_folder='templates')

from . import routes