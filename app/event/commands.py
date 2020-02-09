import os
from glob import glob
from subprocess import call

import click
from flask import Blueprint, Flask
from flask import current_app as app
from flask.cli import with_appcontext

from ..utils.task_handler import task_runner

app = Flask(__name__)

events_commands_blueprint = Blueprint("events_commands", __name__)


@app.cli.command("taskrunner")
def process_tasks():
    task_runner()
    exit()
