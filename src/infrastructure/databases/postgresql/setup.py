from psycopg import OperationalError

from .connection import postgresql_connection
from .schema import (
    create_accounts_table,
    create_file_type,
    create_product_file_table,
    create_product_status_type,
    create_product_table,
    create_role_type,
    create_spaces_table,
    create_users_table,
    create_warranty_type_enum,
    drop_tables,
    drop_types,
)


def create_entities() -> None:
    connection = postgresql_connection()
    with connection.cursor() as cursor:
        try:
            cursor.execute(drop_tables())
            cursor.execute(drop_types())
            cursor.execute(create_role_type())
            cursor.execute(create_file_type())
            cursor.execute(create_product_status_type())
            cursor.execute(create_warranty_type_enum())
            cursor.execute(create_spaces_table())
            cursor.execute(create_users_table())
            cursor.execute(create_accounts_table())
            cursor.execute(create_product_table())
            cursor.execute(create_product_file_table())
            connection.commit()
            cursor.close()
        except OperationalError as e:
            print(e)
            print("An error occurred while creating the tables")
    connection.close()


def setup() -> None:
    create_entities()
