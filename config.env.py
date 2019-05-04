import os

# Flask config
DEBUG = False
IP = os.environ.get("IP", "0.0.0.0")
PORT = os.environ.get("PORT", "8080")
SERVER_NAME = os.environ.get("SERVER_NAME", "localhost:8080")
SECRET_KEY = os.environ.get("SECRET_KEY", "[secret]")

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URI", "mysql+pymysql://hoby-feedback:password@mysql.csh.rit.edu/hoby-feedback"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

