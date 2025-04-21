import os

#replace this locally with your sql user and pswd
class DBLogin:
    USER = "user"
    PSWD = "pswd"

class Config:
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DBLogin.USER}:{DBLogin.PSWD}@localhost/labels'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SVELTE_URI = "http://35.188.116.129:5173"

