import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from twilio.rest import Client

app = Flask(__name__,
            static_folder='../public',
            template_folder='../static')

if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

twilio = Client(app.config["TWILIO_SID"], app.config["TWILIO_TOKEN"])

from .models import *
from .routes import *


@login_manager.user_loader
def load_user(id):
    return Volunteer.query.get(int(id))