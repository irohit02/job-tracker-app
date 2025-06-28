from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    jobs       = db.relationship("Job", backref="owner", lazy=True)

class Job(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    company      = db.Column(db.String(120), nullable=False)
    role         = db.Column(db.String(120), nullable=False)
    link         = db.Column(db.String(255))
    location     = db.Column(db.String(120))
    salary       = db.Column(db.String(120))
    status       = db.Column(db.String(50), default="Applied")
    tags         = db.Column(db.String(255))
    notes        = db.Column(db.Text)
    date_applied = db.Column(db.Date, default=date.today)
    resume_file  = db.Column(db.String(255))
