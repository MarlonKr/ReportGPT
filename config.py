from decouple import config

class Config(object):
    OPENAI_API_KEY = config('OPENAI_API_KEY')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
