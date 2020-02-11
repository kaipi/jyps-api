from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from .event.models import *

from flask_cors import CORS

cors = CORS(supports_credentials=True)

from flask_jwt_simple import JWTManager, jwt_required, create_jwt, get_jwt_identity

jwt = JWTManager()
