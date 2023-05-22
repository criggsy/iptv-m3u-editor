from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_tables():
    from models import Entry, UniqueTvgType, UniqueGroupTitle
    db.create_all()