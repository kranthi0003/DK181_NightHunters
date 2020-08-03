import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SMART-INDIA-HACKATHON-2020'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///G:/Projects/SIH/Project_New/app/db.sqlite3'
    DEBUG = True