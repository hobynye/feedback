from . import db

colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Silver"]
stoplight = ["Red", "Yellow", "Green"]


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(10), nullable=True)


class Role(db.Model):
    year = db.Column(db.Integer, primary_key=True)
    volunteer = db.Column(db.Integer, db.ForeignKey("volunteer.id"), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    color = db.Column(db.Enum(*colors), nullable=True)
    letter = db.Column(db.String(1), nullable=True)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitted_by = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=False)
    color = db.Column(db.Enum(*stoplight), nullable=False)
    datetime = db.Column(db.DateTime, default=db.func.current_timestamp())
