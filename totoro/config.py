import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get(os.path.dirname(__file__)) or 'hallo totoro'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    TOTORO_MAIL_SUBJECT_PREFIX = '[Totoro]'
    TOTORO_MAIL_SENDER = 'Admin <totoro@shibuja.jp>'
    TOTORO_ADMIN = os.environ.get('TOTORO_ADMIN')
    WHOOSH_BASE = os.path.join(basedir, 'search.db')
    MAX_SEARCH_RESULTS = 50

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    DEBUG = True


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    pg_db_username = 'totoro'
    pg_db_password = 'totoro'
    pg_db_name = 'totoro'
    pg_db_hostname = 'localhost'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username,
                                                                                            DB_PASS=pg_db_password,
                                                                                            DB_ADDR=pg_db_hostname,
                                                                                            DB_NAME=pg_db_name)


class TestingConfig(Config):
    TESTING = True
    pg_db_username = 'totoro'
    pg_db_password = 'totoro'
    pg_db_name = 'totoro_test'
    pg_db_hostname = 'localhost'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
