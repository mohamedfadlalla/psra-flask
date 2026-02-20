from flask import Blueprint

hub_bp = Blueprint('hub', __name__, template_folder='templates')

from . import routes