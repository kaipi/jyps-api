import datetime
import string
import random


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
