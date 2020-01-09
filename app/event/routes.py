from flask import Blueprint
from .controllers import *

events_api_blueprint = Blueprint("events_api", "events_api", url_prefix="/api/events")
