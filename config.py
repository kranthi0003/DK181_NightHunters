import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SMART-INDIA-HACKATHON-2020'
    DEVELOPMENT = True

class DevelopmentConfig(Config):
    FLASK_DEBUG = False
