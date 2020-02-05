"""This module is task handler for api
"""
from flask import Flask

from ..event.models import db, Task
from ..taskhandlers import email

app = Flask(__name__)


def task_runner():
    # mainlooop for taskhandler
    tasks = Task.query.filter_by(status=0).all()

    for task in tasks:
        if task.type == 1:
            email.handleEmail(task, db)
        if task.type == 2:
            email.handleEmail(task, db)

        db.session.flush()
