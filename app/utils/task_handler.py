
"""This module is task handler for api
"""
from flask import Flask
from app import Task, db
from flask_mail import Mail, Message
from utils.taskhandlers import email
app = Flask(__name__)
mail = Mail(app)

# mainlooop for taskhandler
tasks = Task.query.filter_by(
    status=0).all()

for task in tasks:
    if task.type == 1:
        email.handleEmail(task)
    if task.type == 2:
        email.handleEmail(task)

    db.session.flush()
