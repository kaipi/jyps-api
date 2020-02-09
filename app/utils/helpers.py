"""Helper functions
"""
import datetime
import random
import string
from functools import wraps

from flask import abort, request
from ..settings.models import Settings


def password_generator(size=8, chars=string.ascii_letters + string.digits):
    """Returns random string for resetted pasword
    
    Keyword Arguments:
        size {int} -- Length of password (default: {8})
        chars {[type]} -- What to use (default: {string.ascii_letters+string.digits})
    
    Returns:
        string -- Random string
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
    """Decorator to require apikey
    
    Arguments:
        view_function {Function} -- Function to decorate
    
    Returns:
        Function -- Decorated function
    """

    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers["X-Api-Key"] == getSetting("apikey"):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


def getSetting(key):
    """Gets settings
    
    Arguments:
        key {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    setting = Settings.query.filter_by(setting_key=key).first()
    return setting.setting_value


def getValidDiscount():
    """Get valid discount for time
    """
