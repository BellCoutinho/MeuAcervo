from __future__ import annotations

from typing import Self
from uuid import UUID

from psycopg import OperationalError, sql

from src.domain.entities import Space
from src.domain.repositories import SpaceRepository
from src.infrastructure.databases.postgresql.connection import postgresql_connection


class SpacePostgreSQLRepository(SpaceRepository):

    def add(self: Self, space: Space) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                INSERT INTO spaces(id, name, address, utility_unit_number, storage_quota, created_at)
                VALUES({id}, {name}, {address}, {ucn}, {quota}, {created_at})
            """).format(
                id=sql.Literal(str(space.id)),
                name=sql.Literal(space.name.name),
                address=sql.Literal(space.address.address),
                ucn=sql.Literal(space.utility_unit_number.number),
                quota=sql.Literal(space.storage_quota),
                created_at=sql.Literal(space.created_at.value),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error adding space: {e}")
        connection.close()

    def find_by_id(self: Self, id: UUID) -> Space | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT id, name, address, utility_unit_number, storage_quota, created_at
                FROM spaces WHERE id = {id}
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = Space.create(
                        id=raw[0], name=raw[1], address=raw[2],
                        utility_unit_number=raw[3], storage_quota=raw[4],
                    ).value
            except OperationalError as e:
                print(f"Error finding space: {e}")
        connection.close()
        return result

    def find_by_user_id(self: Self, user_id: UUID) -> Space | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT s.id, s.name, s.address, s.utility_unit_number, s.storage_quota, s.created_at
                FROM spaces s
                JOIN users u ON u.space_id = s.id
                WHERE u.id = {user_id}
            """).format(user_id=sql.Literal(user_id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = Space.create(
                        id=raw[0], name=raw[1], address=raw[2],
                        utility_unit_number=raw[3], storage_quota=raw[4],
                    ).value
            except OperationalError as e:
                print(f"Error finding space by user: {e}")
        connection.close()
        return result

    def update(self: Self, space: Space) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                UPDATE spaces
                SET name = {name}, address = {address},
                    utility_unit_number = {ucn}, storage_quota = {quota}
                WHERE id = {id}
            """).format(
                id=sql.Literal(str(space.id)),
                name=sql.Literal(space.name.name),
                address=sql.Literal(space.address.address),
                ucn=sql.Literal(space.utility_unit_number.number),
                quota=sql.Literal(space.storage_quota),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error updating space: {e}")
        connection.close()
