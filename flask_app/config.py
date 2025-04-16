import os

class DBLogin:
    USER = "root"
    PSWD = "hrtscybort__"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(f"mysql+pymysql://{DBLogin.USER}:{DBLogin.PSWD}@localhost/labels", "sqlite:///database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

