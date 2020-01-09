import datetime
import string
import random
from functools import wraps
from flask import request, abort


def password_generator(size=8, chars=string.ascii_letters + string.digits):
    """
    Returns a string of random characters
    """
    return "".join(random.choice(chars) for i in range(size))


def dateconvert(o):
    """convert datetime to string, because it's not serializeable by json serializer

    Arguments:
        o {object} -- datetime object

    Returns:
        string -- string presentation of datetime
    """
    if isinstance(o, datetime.date):
        return o.__str__()


def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers["X-Api-Key"] == getSetting("apikey"):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function

def getSetting(key):
    #setting = Settings.query.filter_by(setting_key=key).first()
    #return setting.setting_value
    return "Test"
