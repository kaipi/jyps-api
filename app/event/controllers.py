import hashlib
import json
from decimal import Decimal

import bcrypt
import requests
import simplejson
from flask import Response
from flask import current_app as app
from flask import jsonify, make_response, redirect, request
from flask_jwt_simple import (JWTManager, create_jwt, get_jwt_identity,
                              jwt_required)
from requests.auth import HTTPBasicAuth

from ..utils.helpers import (dateconvert, getSetting, getValidDiscount,
                             password_generator, require_appkey)
from .models import *


@app.route("/v1/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    username = params.get("username", None)
    password = params.get("password", None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user = User.query.filter_by(username=username).first()
    if bcrypt.checkpw(password.encode("utf8"), user.password.encode("utf8")):
        ret = {"jwt": create_jwt(identity=username)}
        return jsonify(ret), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@app.route("/v1/event/", methods=["GET"])
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
        x.append(
            {
                "id": item.id,
                "location": item.location,
                "date": item.date,
                "name": item.name,
                "googlemaps_link": item.googlemaps_link,
                "close_date": item.close_date,
                "open_date": item.open_date,
            }
        )
    data = json.dumps([dict(y) for y in x], default=dateconvert)
    response = make_response(data)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/api/events/v1/event/<int:id>", methods=["PUT"])
@jwt_required
def updateevent(id):  
    """Update event data

    Decorators:
        app

    Returns:
        ok/not ok
    """
    request_data = request.json
    event = Event.query.get(id)
    event.name = request_data["name"]
    event.close_date = request_data["close_date"]
    event.date = request_data["date"]
    event.email_template = request_data["email_template"]
    event.general_description = request_data["general_description"]
    event.groups_description = request_data["groups_description"]
    event.location = request_data["location"]
    event.open_date = request_data["open_date"]
    event.payment_description = (request_data["payment_description"],)
    event.paytrail_product = (request_data["paytrail_product"],)
    event.googlemaps_link = (request_data["googlemaps_link"],)
    # event.event_active = request_data["event_active"],
    event.sport_voucher_email = (request_data["sport_voucher_email"],)
    event.sport_voucher_confirmed_email = request_data["sport_voucher_confirmed_email"]
    i = 0
    for group in event.groups:
        # TODO: Tidy this crap up
        x = request_data["groups"]
        z = x[i]
        group.name = z["name"]
        group.distance = z["distance"]
        group.number_prefix = z["number_prefix"]
        group.price_prepay = z["price_prepay"]
        group.price = z["price"]
        group.product_code = z["product_code"]
        group.racenumberrange_start = z["racenumberrange_start"]
        group.racenumberrange_end = z["racenumberrange_end"]
        group.tagrange_end = z["tagrange_end"]
        group.tagrange_start = z["tagrange_start"]
        # if tagranges are modified, also start has to be updated
        group.current_racenumber = z["current_racenumber"]
        group.current_tag = z["current_tag"]
        group.discount = z["discount"]
        i = i + 1
    db.session.commit()
    
    response = make_response("Event updated", 200)
    return response


@app.route("/api/events/v1/event/<int:id>", methods=["GET"])
def oneevent(id):
    """Get event data

    Decorators:
        app

    Returns:
        json -- json object of one event
    """
    event = Event.query.get(id)
    event_active = True
    close_datetime = datetime.combine(event.close_date, datetime.min.time())

    if close_datetime < datetime.now():
        event_active = False
    groups = []
    discounts = []
    discount_amt = 0
    discount = DiscountStep.query.filter(DiscountStep.event_id == id, DiscountStep.valid_from <= datetime.now(),DiscountStep.valid_to >= datetime.now()).first()
    if discount != None:
        discount_amt = discount.discount_amount
    event_discount = DiscountStep.query.filter(DiscountStep.event_id == id).all()

    for disc in event_discount:
        discounts.append({
            "discount_amount": simplejson.dumps(disc.discount_amount),
            "valid_from": disc.valid_from,
            "valid_to": disc.valid_to
        })
    for group in event.groups:
        groups.append(
            {
                "id": group.id,
                "name": group.name,
                "distance": simplejson.dumps(group.distance),
                "price_prepay": simplejson.dumps(group.price_prepay - discount_amt),
                "price": simplejson.dumps(group.price),
                "product_code": group.product_code,
                "number_prefix": group.number_prefix,
                "tagrange_start": group.tagrange_start,
                "tagrange_end": group.tagrange_end,
                "racenumberrange_start": group.racenumberrange_start,
                "racenumberrange_end": group.racenumberrange_end,
                "discount": simplejson.dumps(group.discount),
                "current_racenumber": group.current_racenumber,
                "current_tag": group.current_tag,
            }
        )
    
    response = {
        "id": event.id,
        "location": event.location,
        "general_description": event.general_description,
        "date": event.date,
        "payment_description": event.payment_description,
        "groups_description": event.groups_description,
        "name": event.name,
        "groups": groups,
        "email_template": event.email_template,
        "close_date": event.close_date,
        "open_date": event.open_date,
        "paytrail_product": event.paytrail_product,
        "googlemaps_link": event.googlemaps_link,
        "sport_voucher_email": event.sport_voucher_email,
        "sport_voucher_confirmed_email": event.sport_voucher_confirmed_email,
        "event_active": event_active,
        "discount_steps": discounts
    }
    data = json.dumps(response, default=dateconvert)
    r = make_response(data)
    r.headers["Content-Type"] = "application/json"
    return r


@app.route("/api/events/v1/event", methods=["POST"])
@jwt_required
def createevent():
    """Create new event

    Decorators:
        app

    Returns:
        String -- OK or Error description
    """
    request_data = request.json
    event = Event(
        name=request_data["name"],
        location=request_data["location"],
        date=request_data["date"],
        general_description=request_data["general_description"],
        groups_description=request_data["groupsDescription"],
        googlemaps_link=request_data["googlemaps_link"],
        paytrail_product=request_data["paytrail_product"],
        email_template=request_data["email_template"],
        payment_description=request_data["paymentDescription"],
        close_date=request_data["close_date"],
        open_date=request_data["open_date"],
    )
    for item in request_data["groups"]:
        group = Group(
            name=item["name"],
            distance=item["distance"],
            price_prepay=Decimal(item["price_prepay"]),
            price=Decimal(item["price"]),
            product_code=item["product_code"],
            number_prefix=item["number_prefix"],
            tagrange_start=int(item["tagrange_start"]),
            tagrange_end=int(item["tagrange_end"]),
            current_tag=int(item["tagrange_start"]),
            current_racenumber=int(item["racenumberrange_start"]),
            racenumberrange_end=int(item["racenumberrange_end"]),
            racenumberrange_start=int(
                item["racenumberrange_start"], discount=Decimal(item["discount"])
            ),
        )
        event.groups.append(group)

    db.session.add(event)
    db.session.commit()
    response = make_response("Event created", 200)
    return response


@app.route("/api/events/v1/event/<int:id>", methods=["DELETE"])
@jwt_required
def deleteevent(id):
    """Delete event

    Decorators:
        app

    Returns:
        String -- Delete one event
    """
    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    response = make_response("Event deleted", 200)
    return response


@app.route("/api/events/v1/participant/", methods=["POST"])
@require_appkey
def addparticipant():
    """Add participant

    Decorators:
        app

    Returns:
        String -- Return code, + url for paytrail if paytrail payment is selected
    """
    request_data = request.json
    group = Group.query.get(request_data["groupid"])
    event = Event.query.get(group.event_id)
    if event.valid_from < datetime.now() or datetime.now() > event.valid_to or event.active == False:
        return make_response(400,"Event is closed or not active")
    participant = Participant(
        firstname=request_data["firstname"],
        lastname=request_data["lastname"],
        telephone=request_data["telephone"],
        email=request_data["email"],
        zipcode=request_data["zip"],
        club=request_data["club"],
        streetaddress=request_data["streetaddress"],
        group_id=request_data["groupid"],
        public=request_data["public"],
        payment_type=request_data["paymentmethod"],
        city=request_data["city"],
        birth_year=request_data["birth_year"],
        team=request_data["team"],
        jyps_member=request_data["jyps_member"],
        sport_voucher_name=request_data["sport_voucher_name"],
        payment_confirmed=False,
    )
    db.session.add(participant)
    db.session.commit()
    db.session.flush()
    group = Group.query.get(participant.group_id)
    price = group.price_prepay
    if request_data["jyps_member"]:
        price = group.price_prepay - group.discount
    # set reference
    participant.referencenumber = str(participant.id) + str(group.id) + str(event.id)
    db.session.commit()

    # if payment is to paytrail
    if participant.payment_type == 1:
        paytrail_json = {
            "orderNumber": participant.referencenumber,
            "currency": "EUR",
            "locale": "fi_FI",
            "urlSet": {
                "success": getSetting("PaytrailSuccessURL"),
                "failure": getSetting("PaytrailFailureURL"),
                "pending": "",
                "notification": getSetting("PaytrailSuccessURL"),
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
                        "country": "FI",
                    },
                },
                "products": [
                    {
                        "title": group.name,
                        "code": event.paytrail_product,
                        "amount": 1,
                        "price": simplejson.dumps(Decimal(price), use_decimal=True),
                        "vat": "0.00",
                        "discount": "0.00",
                        "type": "1",
                    }
                ],
            },
        }
        paytrail_response = requests.post(
            "https://payment.paytrail.com/api-payment/create",
            headers={"X-Verkkomaksut-Api-Version": "1"},
            auth=HTTPBasicAuth(
                getSetting("PaytrailMerchantId"), getSetting("PaytrailMerchantSecret")
            ),
            json=paytrail_json,
        )
        response = make_response(json.dumps(paytrail_response.json()), 200)
        response.headers["Content-Type"] = "application/json"
        db.session.commit()
        return response
    # payment is sport voucher
    if participant.payment_type == 2:
        task = Task(
            target=participant.email, param=event.sport_voucher_email, status=0, type=1
        )
        return redirect(
            "https://tapahtumat.jyps.fi/event/"
            + str(group.event_id)
            + "/eventinfo/?sport_voucher_received=true",
            code=302,
        )

    task = Task(target=participant.email, param=event.email_template, status=0, type=1)

    db.session.add(task)
    db.session.commit()
    response = make_response(json.dumps({"msg": "Added ok", "type": "normal"}), 200)
    return response


@app.route("/api/events/v1/pos/participant/", methods=["POST"])
@jwt_required
def addparticipant_pos():
    """Add participant from POS

    Decorators:
        app

    Returns:
        String -- Return code
    """
    request_data = request.json
    group = Group.query.get(request_data["groupid"])
    racenumber = group.current_racenumber
    racetagnumber = group.current_tag
    db.session.commit()
    participant = Participant(
        firstname=request_data["firstname"],
        lastname=request_data["lastname"],
        telephone=request_data["telephone"],
        email=request_data["email"],
        zipcode=request_data["zip"],
        club=request_data["club"],
        streetaddress=request_data["streetaddress"],
        group_id=request_data["groupid"],
        number=racenumber,
        tagnumber=racetagnumber,
        public=request_data["public"],
        payment_type=request_data["paymentmethod"],
        payment_confirmed=True,
        city=request_data["city"],
        sport_voucher_name=request_data["sport_voucher_name"],
        birth_year=request_data["birth_year"],
        team=request_data["team"],
        jyps_member=request_data["jyps_member"],
    )
    group.current_tag = group.current_tag + 1
    group.current_racenumber = group.current_racenumber + 1
    db.session.add(participant)
    db.session.commit()
    db.session.flush()
    price = group.price
    if request_data["jyps_member"] == True:
        price = group.price - group.discount

    response = make_response(
        json.dumps(
            {
                "msg": "Added ok",
                "type": "normal",
                "price": str(price),
                "racenumber": group.number_prefix + str(participant.number),
            }
        ),
        200,
    )
    return response


@app.route("/api/events/v1/participant/<int:id>", methods=["DELETE"])
@jwt_required
def deleteparticipant(id):
    """Delete participant

    Decorators:
        app

    Returns:
        String -- Delete one Participant
    """
    participant = Participant.query.get(id)
    db.session.delete(participant)
    db.session.commit()
    response = make_response("Participant deleted", 200)
    return response


@app.route("/api/events/v1/events/<int:id>/participants", methods=["GET"])
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
            onegroup = []
            for participant in group.participants:
                if participant.public == True and participant.payment_confirmed == True:
                    onegroup.append(
                        {
                            "id": participant.id,
                            "firstname": participant.firstname,
                            "lastname": participant.lastname,
                            "group": group.name,
                            "club": participant.club,
                            "number": group.number_prefix + str(participant.number),
                            "payment_confirmed": participant.payment_confirmed,
                            "team": participant.team,
                        }
                    )
            participants.append(onegroup)
        data = json.dumps(participants, default=dateconvert)
        r = make_response(data)
        r.headers["Content-Type"] = "application/json"
        return r
    except AttributeError:
        return make_response("No participants found", 503)


@app.route("/api/events/v1/events/<int:id>/participants_pos", methods=["GET"])
@jwt_required
def eventparticipants_pos(id):
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
            onegroup = []
            for participant in group.participants:
                onegroup.append(
                    {
                        "id": participant.id,
                        "firstname": participant.firstname,
                        "lastname": participant.lastname,
                        "group": group.name,
                        "club": participant.club,
                        "streetaddress": participant.streetaddress,
                        "email": participant.email,
                        "telephone": participant.telephone,
                        "zipcode": participant.zipcode,
                        "city": participant.city,
                        "number": group.number_prefix + str(participant.number),
                        "payment_confirmed": participant.payment_confirmed,
                        "team": participant.team,
                    }
                )
            participants.append(onegroup)
        data = json.dumps(participants, default=dateconvert)
        r = make_response(data)
        r.headers["Content-Type"] = "application/json"
        return r
    except AttributeError:
        return make_response("No participants found", 503)


@app.route(
    "/api/events/v1/events/movegroup/<int:participant_id>/<int:new_group>",
    methods=["PATCH"],
)
@jwt_required
def moveparticipant_group(participant_id, new_group):
    """Move participant to other group inside event

    Decorators:
        app

    Returns:
        http -- 200 OK
    """
    group = Group.query.get(new_group)
    participant = Participant.query.get(participant_id)
    racenumber = group.current_racenumber
    racetagnumber = group.current_tag
    group.current_tag = group.current_tag + 1
    group.current_racenumber = group.current_racenumber + 1
    participant.number = racenumber
    participant.tagnumber = racetagnumber
    participant.referencenumber = (
        str(participant.id) + str(group.id) + str(group.event_id)
    )
    participant.group_id = group.id
    db.session.commit()
    return make_response("Participant moved", 200)


@app.route("/api/events/v1/paymentconfirm", methods=["GET"])
def paymentconfirm():
    """Return from succesfull payment + notification url

    Decorators:
        app

    Returns:
        json -- json object of events participants
    """
    returndata = (
        request.args.get("ORDER_NUMBER")
        + "|"
        + request.args.get("TIMESTAMP")
        + "|"
        + request.args.get("PAID")
        + "|"
        + request.args.get("METHOD")
        + "|"
        + getSetting("PaytrailMerchantSecret")
    )

    participant = Participant.query.filter_by(
        referencenumber=request.args.get("ORDER_NUMBER")
    ).first()
    group = Group.query.get(participant.group_id)
    event = Event.query.get(group.event_id)
    if (
        participant.payment_confirmed != True
        and request.args.get("RETURN_AUTHCODE")
        == hashlib.md5(returndata.encode("utf-8")).hexdigest().upper()
    ):
        # racenumbers only if payment is ok
        racenumber = group.current_racenumber
        racetagnumber = group.current_tag
        participant.payment_confirmed = True
        participant.number = racenumber
        participant.tagnumber = racetagnumber
        group.current_tag = group.current_tag + 1
        group.current_racenumber = group.current_racenumber + 1
        task = Task(
            target=participant.email, param=event.email_template, status=0, type=1
        )
        db.session.add(task)
        db.session.commit()
        return redirect(
            "https://tapahtumat.jyps.fi/event/"
            + str(group.event_id)
            + "/eventinfo/?payment_confirmed=true",
            code=302,
        )
    else:
        return redirect(
            "https://tapahtumat.jyps.fi/event/"
            + str(group.event_id)
            + "/eventinfo/?payment_confirmed=false",
            code=302,
        )


@app.route("/api/events/v1/paymentcancel", methods=["GET"])
def paymentcancel():
    """Return from cancelled payment

    Decorators:
        app

    Returns:
        json -- json object of events participants
    """
    participant = Participant.query.filter_by(
        referencenumber=request.args.get("ORDER_NUMBER")
    ).first()
    group = Group.query.get(participant.group_id)

    return redirect(
        "https://tapahtumat.jyps.fi/event/"
        + str(group.event_id)
        + "/eventinfo/?payment_confirmed=false",
        code=302,
    )





@app.route("/api/events/v1/users/allusers", methods=["GET"])
@jwt_required
def allusers():
    """Get all user data

    Decorators:
        app

    Returns:
        json -- json array of object(s) containing all events
    """
    res = User.query.all()
    x = []
    for item in res:
        x.append(
            {
                "id": item.id,
                "username": item.username,
                "email": item.email,
                "realname": item.realname,
            }
        )
    data = json.dumps([dict(y) for y in x], default=dateconvert)
    response = make_response(data)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/api/events/v1/users/add", methods=["POST"])
@jwt_required
def adduser():
    """Add user

    Decorators:
        app

    Returns:
        String -- Return code
    """
    request_data = request.json
    password = password_generator()
    password_crypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(
        username=request_data["username"],
        password=password_crypted,
        email=request_data["email"],
        realname=request_data["fullname"],
    )
    task = Task(
        target=request_data["email"],
        param="Salasanasi ja kayttajatunnuksesi Jyps Ry:n tapahtumajarjestelmaan on: "
        + request_data["username"]
        + "/"
        + password,
        status=0,
        type=2,
    )
    db.session.add(task)
    db.session.add(user)
    db.session.commit()
    response = make_response("User added", 200)
    return response


@app.route("/api/events/v1/users/delete/<int:id>", methods=["DELETE"])
@jwt_required
def deleteuser(id):
    """Delete user

    Decorators:
        app

    Returns:
        String -- Delete one User
    """
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    response = make_response("User deleted", 200)
    return response


@app.route("/api/events/v1/users/resetpassword/<int:id>", methods=["POST"])
@jwt_required
def resetpassword(id):
    """Reset user password

    Decorators:
        app

    Returns:
        OK if resetted 
    """

    user = User.query.get(id)
    # generate new password and send it via email
    password = password_generator()
    password_crypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user.password = password_crypted
    task = Task(
        target=user.email,
        param="Salasanasi ja kayttajatunnuksesi Jyps Ry:n tapahtumajarjestelmaan on: "
        + user.username
        + "/"
        + password,
        status=0,
        type=2,
    )
    db.session.add(task)
    db.session.commit()
    response = make_response("User password reset", 200)
    return response


@app.route("/api/events/v1/<int:id>/chrono", methods=["GET"])
@jwt_required
def getchronocsv(id):
    """Get J2C compatible csv out of participants

    Decorators:
        app

    Returns:
        String - csv of participants for Chrono
    """

    event = Event.query.get(id)
    csv = (
        "FIRST_NAME;LAST_NAME;CLASS;NUMBER;CITY;SPONSOR;MAKE;CLUB;ENGINE;EMAIL;TRANSPONDER"
        + "\n"
    )
    for group in event.groups:
        for participant in group.participants:
            if participant.payment_confirmed == True:
                participant_club_team_separator = "/"
                if participant.club == "" or participant.team == "":
                    participant_club_team_separator = ""
                csv = (
                    csv
                    + participant.firstname
                    + ";"
                    + participant.lastname
                    + ";"
                    + group.name
                    + "("
                    + group.number_prefix
                    + ");"
                    + str(participant.number)
                    + ";"
                    + participant.city
                    + ";;;"
                    + participant.club
                    + participant_club_team_separator
                    + participant.team
                    + ";;"
                    + participant.email
                    + ";"
                    + participant.tagnumber
                    + "\n"
                )
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=chrono.csv"},
    )


@app.route("/api/events/v1/deletegroup/<int:id>", methods=["DELETE"])
@jwt_required
def deletegroup(id):
    """Delete group

    Decorators:
        app

    Returns:
       200 if was deleted ok
    """
    group = Group.query.get(id)
    db.session.delete(group)
    db.session.commit()
    response = make_response("Group deleted", 200)
    return response


@app.route("/api/events/v1/addgroup/<int:id>", methods=["POST"])
@jwt_required
def addgroup(id):
    """Add group to existing event

    Decorators:
        app

    Returns:
       200 if was added ok
    """
    request_data = request.json
    event = Event.query.get(id)
    group = Group(
        name=request_data["name"],
        distance=request_data["distance"],
        number_prefix=request_data["number_prefix"],
        price_prepay=Decimal(request_data["price_prepay"]),
        price=Decimal(request_data["price"]),
        product_code=request_data["product_code"],
        racenumberrange_start=int(request_data["racenumberrange_start"]),
        racenumberrange_end=int(request_data["racenumberrange_end"]),
        tagrange_start=int(request_data["tagrange_start"]),
        tagrange_end=int(request_data["tagrange_end"]),
        current_tag=int(request_data["tagrange_start"]),
        current_racenumber=int(request_data["racenumberrange_start"]),
    )
    event.groups.append(group)
    db.session.commit()
    response = make_response("Group added", 200)
    return response


@app.route("/api/events/v1/copygroups/<int:targetid>/<int:sourceid>", methods=["GET"])
@jwt_required
def copygroups(targetid, sourceid):
    """copy groups to existing event

     Decorators:
         app

     Returns:
        200 if was copied ok
     """
    source_event = Event.query.get(sourceid)
    target_event = Event.query.get(targetid)

    for group in source_event.groups:
        cpgrp = Group(
            name=group.name,
            distance=group.distance,
            number_prefix=group.number_prefix,
            price_prepay=group.price_prepay,
            price=group.price,
            product_code=group.product_code,
            racenumberrange_start=group.racenumberrange_start,
            racenumberrange_end=group.racenumberrange_end,
            tagrange_start=group.tagrange_start,
            tagrange_end=group.tagrange_end,
            discount=group.discount,
        )
        target_event.groups.append(cpgrp)
    db.session.commit()

    response = make_response("Groups copied", 200)
    return response


@app.route("/api/events/v1/approvevoucher/<int:participantid>", methods=["GET"])
@jwt_required
def approvevoucher(participantid):
    """Approve sport voucher, send confirmation email
     Decorators:
         app

     Returns:
        200 if updated ok
    """

    participant = Participant.query.get(participantid)
    group = Group.query.get(participant.group_id)
    event = Event.query.get(group.event_id)
    # racenumbers only if payment is ok
    racenumber = group.current_racenumber
    racetagnumber = group.current_tag
    participant.payment_confirmed = True
    participant.number = racenumber
    participant.tagnumber = racetagnumber
    group.current_tag = group.current_tag + 1
    group.current_racenumber = group.current_racenumber + 1
    task = Task(target=participant.email, param=event.email_template, status=0, type=1)

    task = Task(
        target=participant.email,
        param=event.sport_voucher_confirmed_email,
        status=0,
        type=3,
    )
    db.session.add(task)
    db.session.commit()
    response = make_response("Groups copied", 200)
    return response


@app.route("/api/events/v1/sportvoucherpending/<int:eventid>", methods=["GET"])
@jwt_required
def pendingvouchers(eventid):
    """Get participants with open sportvoucher payment
     Decorators:
         app

     Returns:
        200 if ok
    """
    event = Event.query.get(eventid)
    sport_voucher_participants = []
    for group in event.groups:
        for participant in group.participants:
            if participant.payment_type == 2 and participant.payment_confirmed == False:
                sport_voucher_participants.append(
                    {
                        "id": participant.id,
                        "firstname": participant.firstname,
                        "surname": participant.lastname,
                        "sport_voucher_name": participant.sport_voucher_name,
                        "email": participant.email,
                        "phone": participant.telephone,
                    }
                )
    data = json.dumps(sport_voucher_participants)

    response = make_response(data)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/api/events/v1/recalculate/<int:groupid>", methods=["GET"])
@jwt_required
def recalculate_numbers(groupid):
    """Recalculate numbers for event
     Decorators:
         app

     Returns:
        200 if ok
    """
    group = Group.query.get(groupid)
    group.current_racenumber = group.racenumberrange_start
    group.current_tag = group.tagrange_start

    for participant in group.participants:
        participant.number = group.current_racenumber
        participant.tagnumber = group.current_tag
        group.current_tag = group.current_tag + 1
        group.current_racenumber = group.current_racenumber + 1
        db.session.commit()

    response = make_response("Recalculated", 200)
    return response


@app.route("/api/events/v1/event/<int:eventid>/discount", methods=["GET"])
@jwt_required
def getDiscounts(eventid):
    """Get events discounts

    Arguments:
        eventid {integer} -- Id of event 
    """ 
    discounts = Event.query.get(eventid).all()

    response = make_response(discounts)
    response.headers["Content-Type"] = "application/json"

    return response

@app.route("/api/events/v1/event/<int:eventid>/discount", methods=["POST"])
@jwt_required
def addDiscount(eventid):
    """Add new discount for event
    """
    request_data = request.json
    discount_step = DiscountStep(discount_amount=request_data["discount_amount"],
                                 valid_to=request_data["valid_to"],
                                 valid_from=request_data["valid_from"],
                                 event_id=eventid)
    db.session.add(discount_step)
    db.session.commit()

    return make_response("Discount added", 200)

@app.route("/api/events/v1/event/<int:eventid>/discount/<int:discountid>", methods=["DELETE"])
@jwt_required
def removeDiscount(discountid):
    """Remove one discount

    Arguments:
        discountid {Integer} -- Id of discount record
    """
    discount = DiscountStep.query.get(discountid).first()
    db.session.delete(discount)
    db.session.commit()

    return make_response("Discount removed",200)
