""" Docstring here """
from datetime import datetime
from ..extensions import db


class Data(db.Model):
    """ORM object for cyclist data
    """

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=True)
    qty = db.Column(db.Integer, nullable=True)


class Event(db.Model):
    """ORM object for event data
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=True)
    close_date = db.Column(db.Date, nullable=True)
    open_date = db.Column(db.Date, nullable=True)
    general_description = db.Column(db.Text, nullable=True)
    payment_description = db.Column(db.Text, nullable=True)
    groups_description = db.Column(db.Text, nullable=True)
    googlemaps_link = db.Column(db.Text, nullable=True)
    paytrail_product = db.Column(db.String(11), nullable=True)
    email_template = db.Column(db.Text, nullable=True)
    sport_voucher_email = db.Column(db.Text, nullable=True)
    sport_voucher_confirmed_email = db.Column(db.Text, nullable=True)
    event_active = db.Column(db.Boolean, nullable=True)
    discount_steps = db.relationship(
        "DiscountStep", backref="event", cascade="all, delete, delete-orphan"
    )
    groups = db.relationship(
        "Group", backref="event", cascade="all, delete, delete-orphan"
    )


class Group(db.Model):
    """ORM object for group data
    """

    __tablename__ = "event_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    distance = db.Column(db.Numeric, nullable=True)
    price_prepay = db.Column(db.Numeric, nullable=True)
    price = db.Column(db.Numeric, nullable=True)
    product_code = db.Column(db.String(255), nullable=True)
    number_prefix = db.Column(db.String(255), nullable=True)
    tagrange_start = db.Column(db.Integer, nullable=True)
    tagrange_end = db.Column(db.Integer, nullable=True)
    racenumberrange_start = db.Column(db.Integer, nullable=True)
    racenumberrange_end = db.Column(db.Integer, nullable=True)
    current_tag = db.Column(db.Integer, nullable=True)
    current_racenumber = db.Column(db.Integer, nullable=True)
    discount = db.Column(db.Numeric, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    participants = db.relationship(
        "Participant", backref="event_group", cascade="all, delete, delete-orphan"
    )


class Participant(db.Model):
    """ORM object for participant data
    """

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255), nullable=True)
    lastname = db.Column(db.String(255), nullable=True)
    streetaddress = db.Column(db.String(255), nullable=True)
    zipcode = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    telephone = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    club = db.Column(db.String(255), nullable=True, default="")
    payment_type = db.Column(db.Integer, nullable=True)
    payment_confirmed = db.Column(db.Boolean, nullable=True)
    memo = db.Column(db.Text, nullable=True)
    public = db.Column(db.Boolean, nullable=True)
    tagnumber = db.Column(db.String(255), nullable=True)
    number = db.Column(db.Integer, nullable=True)
    referencenumber = db.Column(db.Integer, nullable=True)
    team = db.Column(db.Text, nullable=True)
    jyps_member = db.Column(db.Boolean, nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("event_group.id"), nullable=False)
    sport_voucher_name = db.Column(db.String(255), nullable=True)


class User(db.Model):
    """ORM object for user data
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    realname = db.Column(db.String(255), nullable=True)


class Task(db.Model):
    """ORM object for task data
    """

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, nullable=True, default=0)
    target = db.Column(db.String(255), nullable=True)
    param = db.Column(db.String(255), nullable=True)
    created = db.Column(db.DateTime, nullable=True, default=datetime.now)
    handled = db.Column(db.DateTime, nullable=True)


class DiscountStep(db.Model):
    """ORM object for discount data
    """

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    discount_amount = db.Column(db.Numeric, nullable=True)
    valid_from = db.Column(db.DateTime, nullable=True, default=datetime.now)
    valid_to = db.Column(db.DateTime, nullable=True, default=datetime.now)
