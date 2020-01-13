from flask import make_response, request, jsonify, Response, redirect
from ..utils.helpers import dateconvert
from .models import *
import json
import requests
import simplejson
from flask_jwt_simple import JWTManager, jwt_required, create_jwt, get_jwt_identity
from flask import current_app as app
from decimal import Decimal
import hashlib


@app.route("/api/events/v1/settings", methods=['GET'])
def allsettings():
    """Get all settings
    Decorators:
        app
    Returns:
        json -- json array of object(s) containing all events
    """
    res = Settings.query.all()
    print(res)
    x = []
    for item in res:
        x.append({"id": item.id,
                  "key": item.setting_key,
                  "value": item.setting_value})
    data = json.dumps([dict(y) for y in x], default=dateconvert)
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route("/api/events/v1/settings", methods=['POST'])
@jwt_required
def addsettings():
    """Add setting
    Decorators:
        app
    Returns:
        String -- Return code
    """
    request_data = request.json
    settings = Settings(
        setting_key=request_data["key"], setting_value=request_data["value"])
    db.session.add(settings)
    db.session.commit()
    response = make_response("Setting added", 200)
    return response


@app.route("/api/events/v1/settings/<int:id>", methods=['DELETE'])
@jwt_required
def deletesettings(id):
    """Delete setting
    Decorators:
        app
    Returns:
        String -- Return code
    """
    setting = Settings.query.get(id)
    db.session.delete(setting)
    db.session.commit()
    response = make_response("Setting added", 200)
    return response


@app.route("/api/events/v1/settings/update", methods=['POST'])
@jwt_required
def updatesettings():
    """update setting
    Decorators:
        app
    Returns:
        String -- Return code
    """
    request_data = request.json
    setting = Settings.query.get(request_data["id"])
    setting.value = request_data["value"]
    db.session.commit()
    response = make_response("Setting updated", 200)
    return response
    