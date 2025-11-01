from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(100))
    message = db.relationship("Feedback")
    # points = db.relationship("Point")

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    rating = db.Column(db.SmallInteger) # 1-5 lang
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# class Point(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     points = db.Column(db.Integer)
#     point_date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))