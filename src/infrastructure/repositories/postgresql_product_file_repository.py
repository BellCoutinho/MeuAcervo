from __future__ import annotations

from typing import Self
from uuid import UUID

from psycopg import OperationalError, sql

from src.domain.entities import ProductFile
from src.domain.repositories import ProductFileRepository
from src.infrastructure.databases.postgresql.connection import postgresql_connection


class ProductFilePostgreSQLRepository(ProductFileRepository):

    def add(self: Self, file: ProductFile) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                INSERT INTO product_file(id, file_path, file_name, file_type, file_size,
                    uploaded_at, product_id, user_id)
                VALUES({id}, {file_path}, {file_name}, {file_type}, {file_size},
                    {uploaded_at}, {product_id}, {user_id})
            """).format(
                id=sql.Literal(str(file.id)),
                file_path=sql.Literal(file.file_path),
                file_name=sql.Literal(file.file_name),
                file_type=sql.Literal(file.file_type.file_type.value),
                file_size=sql.Literal(file.file_size.size),
                uploaded_at=sql.Literal(file.uploaded_at.value),
                product_id=sql.Literal(str(file.product_id)) if file.product_id else sql.Literal(None),
                user_id=sql.Literal(str(file.user_id)) if file.user_id else sql.Literal(None),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error adding file: {e}")
        connection.close()

    def find_by_id(self: Self, id: UUID) -> ProductFile | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT id, file_path, file_name, file_type, file_size,
                    uploaded_at, product_id, user_id
                FROM product_file WHERE id = {id}
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = self._map_row_to_file(raw)
            except OperationalError as e:
                print(f"Error finding file: {e}")
        connection.close()
        return result

    def find_by_product_id(self: Self, product_id: UUID) -> list[ProductFile]:
        connection = postgresql_connection()
        result: list[ProductFile] = []
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT id, file_path, file_name, file_type, file_size,
                    uploaded_at, product_id, user_id
                FROM product_file WHERE product_id = {product_id}
            """).format(product_id=sql.Literal(product_id))
            try:
                cursor.execute(statement)
                for raw in cursor.fetchall():
                    result.append(self._map_row_to_file(raw))
            except OperationalError as e:
                print(f"Error finding files: {e}")
        connection.close()
        return result

    def find_all_by_user(self: Self, user_id: UUID) -> list[ProductFile]:
        connection = postgresql_connection()
        result: list[ProductFile] = []
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT id, file_path, file_name, file_type, file_size,
                    uploaded_at, product_id, user_id
                FROM product_file WHERE user_id = {user_id}
            """).format(user_id=sql.Literal(user_id))
            try:
                cursor.execute(statement)
                for raw in cursor.fetchall():
                    result.append(self._map_row_to_file(raw))
            except OperationalError as e:
                print(f"Error finding files: {e}")
        connection.close()
        return result

    def sum_size_by_user(self: Self, user_id: UUID) -> int:
        connection = postgresql_connection()
        result = 0
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT COALESCE(SUM(file_size), 0) FROM product_file WHERE user_id = {user_id}
            """).format(user_id=sql.Literal(user_id))
            try:
                cursor.execute(statement)
                result = cursor.fetchone()[0]
            except OperationalError as e:
                print(f"Error summing size: {e}")
        connection.close()
        return result

    def remove_by_id(self: Self, id: UUID) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("DELETE FROM product_file WHERE id = {id}").format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error removing file: {e}")
        connection.close()

    def _map_row_to_file(self, raw: tuple) -> ProductFile:
        from src.domain.value_objects import FileSize, FileTypeVO
        return ProductFile.create(
            id=raw[0], file_path=raw[1], file_name=raw[2],
            file_type=raw[3], file_size=raw[4],
            product_id=raw[6], user_id=raw[7],
        ).value
