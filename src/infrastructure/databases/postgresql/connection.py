import time

from psycopg import Connection, OperationalError
from psycopg.conninfo import make_conninfo
from psycopg_pool import ConnectionPool

from src.infrastructure.databases.postgresql.settings import PGSettings

_pool: ConnectionPool | None = None

_MAX_RETRIES = 10
_RETRY_DELAY = 2


def postgresql_connection():
    for attempt in range(_MAX_RETRIES):
        try:
            pg_connection = Connection.connect(
                dbname=PGSettings.DATABASE_NAME,
                user=PGSettings.USER_NAME,
                host=PGSettings.HOST,
                password=PGSettings.PASSWORD,
                port=PGSettings.PORT,
            )
            return pg_connection
        except OperationalError as e:
            if attempt < _MAX_RETRIES - 1:
                print(f"DB connection failed (attempt {attempt + 1}/{_MAX_RETRIES}), retrying in {_RETRY_DELAY}s...")
                time.sleep(_RETRY_DELAY)
            else:
                raise e


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        for attempt in range(_MAX_RETRIES):
            try:
                _pool = ConnectionPool(
                    make_conninfo(
                        dbname=PGSettings.DATABASE_NAME,
                        user=PGSettings.USER_NAME,
                        host=PGSettings.HOST,
                        password=PGSettings.PASSWORD,
                        port=PGSettings.PORT,
                    ),
                    min_size=5,
                    max_size=10,
                )
                return _pool
            except Exception as e:
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(_RETRY_DELAY)
                else:
                    raise e
    return _pool
