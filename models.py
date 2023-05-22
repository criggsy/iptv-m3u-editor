from db import db

class Entry(db.Model):
    __tablename__ = 'entry'
    id = db.Column(db.Integer, primary_key=True)
    tvg_type = db.Column(db.String(50), nullable=False)
    group_title = db.Column(db.String(100), nullable=False)
    tvg_name = db.Column(db.String(100))
    tvg_logo = db.Column(db.String(100))
    metadata_value = db.Column(db.String(255))
    url = db.Column(db.String(255))
    channel_number = db.Column(db.Integer)
    tvg_id = db.Column(db.String(50))

class UniqueTvgType(db.Model):
    __tablename__ = 'unique_tvg_type'
    id = db.Column(db.Integer, primary_key=True)
    tvg_type = db.Column(db.String(50), unique=True, nullable=False)

class UniqueGroupTitle(db.Model):
    __tablename__ = 'unique_group_title'
    id = db.Column(db.Integer, primary_key=True)
    group_title = db.Column(db.String(100), unique=True, nullable=False)
