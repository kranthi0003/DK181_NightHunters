import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SMART-INDIA-HACKATHON-2020'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///E:/workspace/Projects/Quester/app/db.sqlite3'
    DEBUG = True