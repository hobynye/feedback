from . import db

COLORS = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Silver"]
STOPLIGHT = ["Red", "Yellow", "Green"]


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(10), nullable=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(150), nullable=True)
    alert = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, email, phone, password):
        self.name = name
        self.password = password
        self.email = email
        self.phone = phone

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name


class Role(db.Model):
    year = db.Column(db.Integer, primary_key=True)
    volunteer = db.Column(db.Integer, db.ForeignKey("volunteer.id"), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    color = db.Column(db.Enum(*COLORS), nullable=True)
    letter = db.Column(db.String(3), nullable=True)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitted_by = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=False)
    color = db.Column(db.Enum(*STOPLIGHT), nullable=False)
    response = db.Column(db.Boolean, nullable=False, default=False)
    datetime = db.Column(db.DateTime, default=db.func.current_timestamp())
    body = db.Column(db.Text, nullable=False)
    handled = db.Column(db.Boolean, nullable=False, default=False)
