"""
App init module


@author: Timo Kaipiainen
"""
import logging
import logging.handlers

from flask import Flask, jsonify, redirect, render_template
from flask_migrate import Migrate

from .extensions import cors, db, jwt


def create_app():
    """Initiate flask app"""
    app = Flask(
        __name__,
        instance_relative_config=False,
        instance_path="/Users/kaipi/Desktop/Projects/jyps-api",
    )
    app.config.from_pyfile("../instance/config.py")
    # login
    handler = logging.handlers.RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=app.config["LOG_SIZE"]
    )
    handler.setLevel(app.config["LOG_LEVEL"])
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(pathname)s at %(lineno)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    logging.getLogger("flask_cors").level = logging.DEBUG

    # init flask-extensions
    cors.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():

        from .event.routes import events_api_blueprint
        from .settings.routes import settings_api_blueprint
        from .event.commands import events_commands_blueprint

        app.register_blueprint(events_api_blueprint)
        app.register_blueprint(settings_api_blueprint)
        app.register_blueprint(events_commands_blueprint)
        db.create_all()
    return app
