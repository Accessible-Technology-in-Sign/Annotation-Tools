import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("mysql+pymysql://jq:password@localhost/labels", "sqlite:///database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DBLogin:
    USER = "jq"
    PSWD = "password"