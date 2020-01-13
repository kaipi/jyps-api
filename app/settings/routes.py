from flask import Blueprint
from .controllers import *

settings_api_blueprint = Blueprint(
    "settings_api", "settings_api"
)
