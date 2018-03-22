
#!flask/bin/python
"""Handler for jyps-api
"""
import json
import datetime
from flask import Flask, jsonify, make_response, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import simplejson
from requests.auth import HTTPBasicAuth
from decimal import *
from functools import wraps

from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
from flask_migrate import Migrate
from flask_sendmail import Mail
from flask_sendmail import Message
import bcrypt
import hashlib
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jypsdata:jypsdata123@localhost/jypsdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_MAILER'] = '/usr/sbin/sendmail'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
# Setup the Flask-JWT-Simple extension
app.config['JWT_SECRET_KEY'] = "SEEECRET"  # Change this!
jwt = JWTManager(app)


def dateconvert(o):
    """convert datetime to string, because it's not serializeable by json serializer

    Arguments:
        o {object} -- datetime object

    Returns:
        string -- string presentation of datetime
    """
    if isinstance(o, datetime.date):
        return o.__str__()


def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and request.args.get('key') == getSetting("apikey"):
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


@app.route('/api/events/v1/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    username = params.get('username', None)
    password = params.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user = User.query.filter_by(username=username).first()
    if bcrypt.checkpw(password.encode("utf8"), user.password.encode("utf8")):
        ret = {'jwt': create_jwt(identity=username)}
        return jsonify(ret), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@app.route("/api/data/v1/cyclistdata", methods=['GET'])
def cyclistdata():
    """Get all cyclist data

    Decorators:
        app

    Returns:
        json -- json object containing all measurement data
    """
    res = Data.query.all()
    x = []
    for item in res:
        x.append({"id": item.id, "location": item.location,
                  "cyclist_qty": item.qty, "date": item.date})
    data = json.dumps([dict(y) for y in x], default=dateconvert)
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route("/api/events/v1/event/allevents", methods=['GET'])
def allevents():
    """Get all event data

    Decorators:
        app

    Returns:
        json -- json array of object(s) containing all events
    """
    res = Event.query.all()
    x = []
    for item in res:
        x.append({"id": item.id,
                  "location": item.location,
                  "date": item.date,
                  "name": item.name,
                  "googlemaps_link": item.googlemaps_link})
    data = json.dumps([dict(y) for y in x], default=dateconvert)
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route("/api/events/v1/event/<int:id>", methods=['GET'])
def oneevent(id):
    """Get event data

    Decorators:
        app

    Returns:
        json -- json object of one event
    """
    event = Event.query.get(id)
    groups = []
    for group in event.groups:
        groups.append({"id": group.id, "name": group.name, "distance": simplejson.dumps(Decimal(group.distance)),
                       "price_prepay": simplejson.dumps(Decimal(group.price_prepay)), "price": simplejson.dumps(Decimal(group.price)), "product_code": group.product_code, "number_prefix": group.number_prefix, "tagrange_start": group.tagrange_start, "tagrange_end": group.tagrange_end, "current_tag": group.current_tag})
    response = ({"id": event.id, "location": event.location,
                 "general_description": event.general_description, "date": event.date, "payment_description": event.payment_description,
                 "groups_description": event.groups_description, "name": event.name, "groups": groups})
    data = json.dumps(response,  default=dateconvert)
    r = make_response(data)
    r.headers['Content-Type'] = 'application/json'
    return r


@app.route("/api/events/v1/createevent", methods=['POST'])
def createevent():
    """Create new event

    Decorators:
        app

    Returns:
        String -- OK or Error description
    """
    request_data = request.json
    event = Event(name=request_data["name"], location=request_data["location"], date=request_data["date"], general_description=request_data["description"],
                  groups_description=request_data["groupsDescription"], googlemaps_link=request_data[
                      "googlemaps_link"], paytrail_product=request_data["paytrail_product"],
                  email_template=request_data["email_template"], payment_description=request_data["paymentDescription"])
    for item in request_data["groups"]:
        group = Group(name=item["name"], distance=item["distance"],
                      price_prepay=Decimal(item["price_prepay"]), price=Decimal(item["price"]), product_code=item["product_code"],
                      number_prefix=item["number_prefix"], tagrange_start=int(
                          item["tagrange_start"]),
                      tagrange_end=int(item["tagrange_end"]), current_tag=int(item["tagrange_start"]), current_racenumber=int(item["racenumberrange_start"]),
                      racenumberrange_end=int(item["racenumberrange_end"]), racenumberrange_start=int(item["racenumberrange_start"]))
        event.groups.append(group)

    db.session.add(event)
    db.session.commit()
    response = make_response("Event created", 200)
    return response


@app.route("/api/events/v1/deleteevent", methods=['DELETE'])
def deleteevent():
    """Delete event

    Decorators:
        app

    Returns:
        String -- Delete one event
    """
    request_data = request.json
    event = Event.query.get(request_data["id"])
    db.session.delete(event)
    db.session.commit()
    response = make_response("Event deleted", 200)
    return response


@app.route("/api/events/v1/addparticipant", methods=['POST'])
def addparticipant():
    """Add participant

    Decorators:
        app

    Returns:
        String -- Return code, + url for paytrail if paytrail payment is selected
    """
    request_data = request.json
    group = Group.query.get(request_data["groupid"])
    racenumber = group.number_prefix + str(group.current_racenumber)
    racetagnumber = group.current_tag
    group.current_tag = group.current_tag + 1
    group.current_racenumber = group.current_racenumber + 1
    db.session.commit()
    participant = Participant(firstname=request_data["firstname"], lastname=request_data["lastname"], telephone=request_data["telephone"], email=request_data["email"],
                              zipcode=request_data["zip"], club=request_data["club"], streetaddress=request_data[
        "streetaddress"], group_id=request_data["groupid"],
        number=racenumber, tagnumber=racetagnumber, public=request_data["public"], payment_type=request_data["paymentmethod"])
    db.session.add(participant)
    db.session.commit()
    group = Group.query.get(participant.group_id)
    event = Event.query.get(group.event_id)
    # if payment is to paytrail
    if participant.payment_type == 1:
        paytrail_json = {
            "orderNumber": participant.id,
            "currency": "EUR",
            "locale": "fi_FI",
            "urlSet": {
                "success": getSetting("PaytrailSuccessURL"),
                "failure": getSetting("PaytrailFailureURL"),
                "pending": "",
                "notification": getSetting("PaytrailSuccessURL")
            },
            "orderDetails": {
                "includeVat": "1",
                "contact": {
                    "telephone": participant.telephone,
                    "mobile": participant.telephone,
                    "email": participant.email,
                    "firstName": participant.firstname,
                    "lastName": participant.lastname,
                    "companyName": "",
                    "address": {
                        "street": participant.streetaddress,
                        "postalCode": participant.zipcode,
                        "postalOffice": "Jyvaskyla",
                        "country": "FI"
                    }
                },
                "products": [
                    {
                        "title": group.name,
                        "code": event.paytrail_product,
                        "amount": 1,
                        "price": simplejson.dumps(Decimal(group.price_prepay), use_decimal=True),
                        "vat": "24.00",
                        "discount": "0.00",
                        "type": "1"
                    }
                ]
            }
        }
        paytrail_response = requests.post(
            "https://payment.paytrail.com/api-payment/create",
            headers={'X-Verkkomaksut-Api-Version': '1'},
            auth=HTTPBasicAuth(getSetting("PaytrailMerchantId"),
                               getSetting("PaytrailMerchantSecret")),
            json=paytrail_json)
        response = make_response(json.dumps(paytrail_response.json()), 200)
        response.headers['Content-Type'] = 'application/json'
        task = Task(target=participant.email,
                    param=event.email_template,  status=0, type=1)
        return response

    task = Task(target=participant.email, param=event.email_template,
                status=0, type=1)

    db.session.add(task)
    db.session.commit()
    response = make_response(json.dumps(
        {"msg": "Added ok", "type": "normal"}), 200)
    return response


@app.route("/api/events/v1/deleteparticipant", methods=['DELETE'])
def deleteparticipant():
    """Delete participant

    Decorators:
        app

    Returns:
        String -- Delete one Participant
    """
    request_data = request.json
    participant = Participant.query.get(request_data["id"])
    db.session.delete(participant)
    db.session.commit()
    response = make_response("Participant deleted", 200)
    return response


@app.route("/api/events/v1/events/<int:id>/participants", methods=['GET'])
def eventparticipants(id):
    """Get participants of event

    Decorators:
        app

    Returns:
        json -- json object of events participants
    """
    try:
        event = Event.query.get(id)
        participants = []
        for group in event.groups:
            for participant in group.participants:
                if participant.public == True:
                    participants.append({"id": participant.id, "firstname": participant.firstname,
                                         "lastname": participant.lastname, "group": group.name, "club": participant.club,
                                         "number": participant.number, "payment_confirmed": participant.payment_confirmed})

        data = json.dumps(participants,  default=dateconvert)
        r = make_response(data)
        r.headers['Content-Type'] = 'application/json'
        return r
    except AttributeError:
        return make_response("No participants found", 503)


@app.route("/api/events/v1/paymentconfirm", methods=['GET'])
def paymentconfirm():
    """Return from succesfull payment + notification url

    Decorators:
        app

    Returns:
        json -- json object of events participants
    """

    returndata = request.form['ORDER_NUMBER'] + "|" + request.form['TIMESTAMP'] + "|" + \
        request.form['PAID'] + "|" + request.form['METHOD'] + \
        "|" + getSetting("PaytrailMerchantSecret")

    returndata = returndata.upper()

    if getSetting("PaytrailMerchantSecret") == hashlib.md5(returndata).hexdigest():
        participant = Participant.query.filter_by(
            reference_number=request.form['ORDER_NUMBER'])
        participant.payment_confirmed = True
        db.session.commit(participant)
        return redirect("https://tapahtumat.jyps.fi", code=302)


@app.route("/api/events/v1/paymentcancel", methods=['GET'])
def paymmentcancel():
    """Return from cancelled payment

    Decorators:
        app

    Returns:
        json -- json object of events participants
    """
    return redirect("https://tapahtumat.jyps.fi", code=302)


@app.route("/api/events/v1/settings", methods=['GET'])
def allsettings():
    """Get all settings

    Decorators:
        app

    Returns:
        json -- json array of object(s) containing all events
    """
    res = Settings.query.all()
    x = []
    for item in res:
        x.append({"id": item.id,
                  "key": item.location,
                  "value": item.date})
    data = json.dumps([dict(y) for y in x], default=dateconvert)
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route("/api/events/v1/settings/add", methods=['POST'])
def addsettings():
    """Add setting

    Decorators:
        app

    Returns:
        String -- Return code
    """
    request_data = request.json
    settings = Participant(
        key=request_data["key"], value=request_data["value"])
    db.session.add(settings)
    db.session.commit()
    response = make_response("Setting added", 200)
    return response


@app.route("/api/events/v1/settings/<int:id>/update", methods=['PUT'])
def updatesettings():
    """update setting

    Decorators:
        app

    Returns:
        String -- Return code
    """
    request_data = request.json
    setting = Settings.query.get(id)
    setting.value = request_data["value"]
    db.session.commit()
    response = make_response("Setting updated", 200)
    return response


@app.route("/api/events/v1/users/add", methods=['POST'])
def adduser():
    """Add user

    Decorators:
        app

    Returns:
        String -- Return code
    """
    request_data = request.json
    user = User(
        username=request_data["username"], password=request_data["password"], email=request_data["email"], realname=request_data["realname"])
    db.session.add(user)
    db.session.commit()
    response = make_response("User added", 200)
    return response


@app.route("/api/events/v1/users/delete", methods=['DELETE'])
def deleteuser():
    """Delete user

    Decorators:
        app

    Returns:
        String -- Delete one User
    """
    request_data = request.json
    user = User.query.get(request_data["id"])
    db.session.delete(user)
    db.session.commit()
    response = make_response("User deleted", 200)
    return response


def getSetting(key):
    setting = Settings.query.filter_by(key=key).first()
    return setting.value


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)


class Data(db.Model):
    """ORM object for cyclist data
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(80), nullable=True)
    date = db.Column(db.Date, nullable=True)
    qty = db.Column(db.Integer, nullable=True)


class Event(db.Model):
    """ORM object for event data
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    location = db.Column(db.String(80), nullable=True)
    date = db.Column(db.Date, nullable=True)
    general_description = db.Column(db.String(80), nullable=True)
    payment_description = db.Column(db.String(80), nullable=True)
    groups_description = db.Column(db.String(80), nullable=True)
    googlemaps_link = db.Column(db.String(250), nullable=True)
    paytrail_product = db.Column(db.String(11), nullable=True)
    email_template = db.Column(db.String(250), nullable=True)
    groups = db.relationship('Group', backref='event',
                             cascade="all, delete, delete-orphan")


class Group(db.Model):
    """ORM object for group data
    """
    __tablename__ = "event_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    distance = db.Column(db.Numeric, nullable=True)
    price_prepay = db.Column(db.Numeric, nullable=True)
    price = db.Column(db.Numeric, nullable=True)
    product_code = db.Column(db.String(80), nullable=True)
    number_prefix = db.Column(db.String(80), nullable=True)
    tagrange_start = db.Column(db.Integer, nullable=True)
    tagrange_end = db.Column(db.Integer, nullable=True)
    racenumberrange_start = db.Column(db.Integer, nullable=True)
    racenumberrange_end = db.Column(db.Integer, nullable=True)
    current_tag = db.Column(db.Integer, nullable=True)
    current_racenumber = db.Column(db.Integer, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    participants = db.relationship('Participant', backref='event_group',
                                   cascade="all, delete, delete-orphan")


class Participant(db.Model):
    """ORM object for participant data
    """
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=True)
    streetaddress = db.Column(db.String(80), nullable=True)
    zipcode = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    telephone = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(80), nullable=True)
    club = db.Column(db.String(80), nullable=True)
    payment_type = db.Column(db.Integer, nullable=True)
    payment_confirmed = db.Column(db.Boolean, nullable=True)
    memo = db.Column(db.String(250), nullable=True)
    public = db.Column(db.Boolean, nullable=True)
    tagnumber = db.Column(db.String(80), nullable=True)
    number = db.Column(db.String(80), nullable=True)
    referencenumber = db.Column(db.Integer,  nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey(
        'event_group.id'), nullable=False)


class Settings(db.Model):
    """ORM object for settings data
    """
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(80), nullable=True)
    setting_value = db.Column(db.String(80), nullable=True)


class User(db.Model):
    """ORM object for user data
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(80), nullable=True)
    realname = db.Column(db.String(80), nullable=True)


class Task(db.Model):
    """ORM object for task data
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, nullable=True, default=0)
    target = db.Column(db.String(80), nullable=True)
    param = db.Column(db.String(80), nullable=True)
    created = db.Column(db.DateTime, nullable=True,
                        default=datetime.datetime.now)
    handled = db.Column(db.DateTime, nullable=True)
