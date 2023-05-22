from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Entry(db.Model):
    __tablename__ = 'entry'
    id = db.Column(db.Integer, primary_key=True)
    tvg_type = db.Column(db.String(50))
    group_title = db.Column(db.String(100))
    tvg_name = db.Column(db.String(100))
    tvg_logo = db.Column(db.String(100))
    metadata_value = db.Column(db.String(255))
    url = db.Column(db.String(255))
    channel_number = db.Column(db.Integer)
    tvg_id = db.Column(db.String(50))
