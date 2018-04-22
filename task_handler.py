
"""This module is task handler for api
"""
from flask import Flask
import datetime
import time
from app import Task, db
from flask_mail import Mail, Message
app = Flask(__name__)
mail = Mail(app)

def handleEmail(task):
    with app.app_context():
       msg = Message("Imoittautumisesi JYPS Ry:n tapahtumaan",
                     sender="noreply@jyps.fi",
                    recipients=[task.target],
                     body=task.param)
       mail.send(msg)
       task.status = 2
       task.handled = datetime.datetime.now()
       db.session.commit()


# mainlooop for taskhandler

while True:
    print("Loop")
    tasks = Task.query.filter_by(
        status=0).all()

    for task in tasks:
        if task.type == 1:
            handleEmail(task)
    db.session.flush()
    time.sleep(30)
