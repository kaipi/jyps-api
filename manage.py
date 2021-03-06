from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.utils.task_handler import task_runner


app = Flask(__name__)
app.config.from_pyfile("./instance/config.py")

db = SQLAlchemy(app)
from app.event.models import *
from app.settings.models import *

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("db", MigrateCommand)


@manager.command
def taskrunner():
    task_runner()


if __name__ == "__main__":
    manager.run()
