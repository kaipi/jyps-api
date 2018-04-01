
"""This module is task handler for api
"""
from flask import Flask
import datetime
import time
from app import Task, db
from flask_sendmail import Mail, Message
app = Flask(__name__)
mail = Mail(app)


def handleEmail(task):
    print "Processing message to: " + task.target
    msg = Message("Imoittautumisesi JYPS Ry:n tapahtumaan",
                  sender="imoittautuminen@jyps.fi",
                  recipients=[task.target],
                  body=task.param)
    mail.send(msg)
    task.status = 2
    db.session.commit()


# mainlooop for taskhandler
i = 0
while True:
    i = i + 1
    print "Loop: " + str(i)
    tasks = Task.query.filter_by(
        status=0).all()

    for task in tasks:
        if task.type == 1:
            handleEmail(task)
    db.session.flush()
    time.sleep(5)
