from flask_sqlalchemy import SQLAlchemy

from app import db

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metadata_value = db.Column(db.String(255))
    url = db.Column(db.String(255))
    tvg_id = db.Column(db.String(255))
    tvg_name = db.Column(db.String(255))
    tvg_logo = db.Column(db.String(255))
    group_title = db.Column(db.String(255))
    channel_number = db.Column(db.Integer)
    tvg_type = db.Column(db.String(255))
