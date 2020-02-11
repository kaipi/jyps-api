import datetime

from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)


def handleEmail(task, db):
    with app.app_context():
        msg = Message(
            "Imoittautumisesi JYPS Ry:n tapahtumaan",
            sender="noreply@jyps.fi",
            recipients=[task.target],
            body=task.param,
        )
        print(msg)
        # mail.send(msg)
        # task.status = 2
        # task.handled = datetime.datetime.now()
        db.session.commit()
        return
