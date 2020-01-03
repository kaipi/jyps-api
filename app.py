#!flask/bin/python
"""Handler for jyps-api
"""
import json
import datetime
from flask import Flask, jsonify, make_response, request, abort, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import simplejson
from requests.auth import HTTPBasicAuth
from decimal import *
from functools import wraps
from flask_jwt_simple import JWTManager, jwt_required, create_jwt, get_jwt_identity
from flask_migrate import Migrate
import bcrypt
import hashlib
from localconfig import jwtkey, dbstring

app = Flask(__name__)
CORS(app)
expire = datetime.timedelta(hours=24)
app.config["SQLALCHEMY_DATABASE_URI"] = dbstring
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_EXPIRES"] = expire
db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db, compare_type=True)
# Setup the Flask-JWT-Simple extension
jwt = JWTManager(app)


app.config["JWT_SECRET_KEY"] = jwtkey  # Change this!


def getSetting(key):
    setting = Settings.query.filter_by(setting_key=key).first()
    return setting.setting_value


def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers["X-Api-Key"] == getSetting("apikey"):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)
