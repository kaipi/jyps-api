
#!flask/bin/python
"""Handler for jyps-api 
"""
import json
import datetime
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import settings
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://somefunnystuff@localhost/jypsdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def dateconvert(o):
    """convert datetime to string, because it's not serializeable by json serializer

    Arguments:
        o {object} -- datetime object

    Returns:
        string -- string presentation of datetime
    """
    if isinstance(o, datetime.date):
        return o.__str__()


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


if __name__ == "__main__":
    application.run(host='0.0.0.0')


class Data(db.Model):
    """ORM object for data
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(80), nullable=True)
    date = db.Column(db.Date, nullable=True)
    qty = db.Column(db.Integer, nullable=True)
