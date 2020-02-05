import os
from glob import glob
from subprocess import call
from flask import Blueprint

import click
from flask import current_app, Flask
from flask.cli import with_appcontext
from ..utils.task_handler import task_runner
from flask import current_app as app

app = Flask(__name__)
events_commands_blueprint = Blueprint("events_commands", "events_commands")


@app.cli.command("taskrunner")
def process_tasks():
    task_runner()
    exit()
