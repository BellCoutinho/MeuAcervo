import os


class PGSettings:
    DATABASE_NAME = os.environ.get('PG_DATABASE_NAME')
    USER_NAME = os.environ.get('PG_USER_NAME')
    PASSWORD = os.environ.get('PG_PASSWORD')
    HOST = os.environ.get('PG_HOST', 'localhost')
    PORT = os.environ.get('PG_PORT', '5432')
