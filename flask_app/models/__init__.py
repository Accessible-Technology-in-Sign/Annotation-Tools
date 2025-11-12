from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Annot(db.Model):
    __tablename__ = "annots"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_path = db.Column(db.String(255), nullable=False)
    sign = db.Column(db.String(255), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    time = db.Column(db.TIMESTAMP, default=datetime)
    label = db.Column(db.String(255), nullable=False)
    comments = db.Column(db.Text)
    timestamp_left_ms = db.Column(db.Integer, nullable=True)
    timestamp_right_ms = db.Column(db.Integer, nullable=True)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)