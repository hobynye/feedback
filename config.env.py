import os

# Flask config
DEBUG = False
IP = os.environ.get("IP", "0.0.0.0")
PORT = os.environ.get("PORT", "8080")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost:8080")
SECRET_KEY = os.environ.get("SECRET_KEY", "[secret]")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

TWILIO_SID = os.environ.get("TWILIO_SID", "account_id")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN", "[secret]")
TWILIO_NUMBER = os.environ.get("TWILIO_PHONE", "+12345678910")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URI", "mysql+pymysql://hoby-feedback:password@mysql.csh.rit.edu/hoby-feedback"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_SIZE = 100
SQLALCHEMY_POOL_RECYCLE = 280

