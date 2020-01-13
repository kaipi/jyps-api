""" Docstring here """
""" Docstring here """
from ..extensions import db

class Settings(db.Model):
    """ORM object for settings data
    """
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(255), nullable=True)
    setting_value = db.Column(db.String(255), nullable=True)
