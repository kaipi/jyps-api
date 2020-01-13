import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


DEBUG = True
Testing = True
JWT_SECRET_KEY = "123123123"  # same key will be used for csrf protection


# database
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@localhost/jypsdata"
# SQLALCHEMY_DATABASE_URI = "mysql://<username>:<password>@<host>/<database>" # mysql/mariadb


# logging
import logging

LOG_FILE = "/tmp/myproject.log"
LOG_SIZE = 1024 * 1024
LOG_LEVEL = logging.DEBUG

