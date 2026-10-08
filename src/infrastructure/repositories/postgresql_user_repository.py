from __future__ import annotations

from typing import Self
from uuid import UUID

from psycopg import OperationalError, sql

from src.domain.entities import Account, User
from src.domain.repositories import UserRepository
from src.domain.value_objects import Role
from src.infrastructure.databases.postgresql.connection import postgresql_connection


class UserPostgreSQLRepository(UserRepository):

    def add(self: Self, user: User, account: Account) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            user_insert = sql.SQL("""
                INSERT INTO users(id, first_name, last_name, role, is_approved, storage_used, space_id)
                VALUES({id}, {first_name}, {last_name}, {role}, {is_approved}, {storage_used}, {space_id})
            """).format(
                id=sql.Literal(str(user.id)),
                first_name=sql.Literal(user.name.first_name),
                last_name=sql.Literal(user.name.last_name),
                role=sql.Literal(user.role.role_type.value),
                is_approved=sql.Literal(user.is_approved),
                storage_used=sql.Literal(user.storage_used),
                space_id=sql.Literal(str(user.space_id)) if user.space_id else sql.Literal(None),
            )
            account_insert = sql.SQL("""
                INSERT INTO accounts(id, email, password, created_at, is_active, user_id)
                VALUES({id}, {email}, {password}, {created_at}, {is_active}, {user_id})
            """).format(
                id=sql.Literal(str(account.id)),
                email=sql.Literal(account.email.address),
                password=sql.Literal(account.password.passphrase),
                created_at=sql.Literal(account.created_at.value),
                is_active=sql.Literal(account.is_active),
                user_id=sql.Literal(str(user.id)),
            )
            try:
                cursor.execute(user_insert)
                cursor.execute(account_insert)
                connection.commit()
            except OperationalError as e:
                print(f"Error adding user: {e}")
            except Exception as e:
                print(f"Error adding user: {e}")
        connection.close()

    def exist_by_email(self: Self, email: str) -> bool:
        connection = postgresql_connection()
        result = False
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT EXISTS (SELECT 1 FROM accounts WHERE email = {email})
            """).format(email=sql.Literal(email))
            try:
                cursor.execute(statement)
                result = cursor.fetchone()[0]
            except OperationalError as e:
                print(f"Error checking email: {e}")
        connection.close()
        return result

    def exist_by_id(self: Self, id: UUID) -> bool:
        connection = postgresql_connection()
        result = False
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT EXISTS (SELECT 1 FROM users WHERE id = {id})
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                result = cursor.fetchone()[0]
            except OperationalError as e:
                print(f"Error checking id: {e}")
        connection.close()
        return result

    def find_by_id(self: Self, id: UUID) -> User | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT u.id, u.first_name, u.last_name, u.role, u.is_approved,
                       u.storage_used, u.space_id
                FROM users u WHERE u.id = {id}
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = User.create(
                        id=raw[0], first_name=raw[1], last_name=raw[2],
                        role=raw[3], is_approved=raw[4], storage_used=raw[5],
                        space_id=raw[6],
                    ).value
            except OperationalError as e:
                print(f"Error finding user: {e}")
        connection.close()
        return result

    def find_by_email(self: Self, email: str) -> User | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT u.id, u.first_name, u.last_name, u.role, u.is_approved,
                       u.storage_used, u.space_id
                FROM users u
                JOIN accounts a ON u.id = a.user_id
                WHERE a.email = {email}
            """).format(email=sql.Literal(email))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = User.create(
                        id=raw[0], first_name=raw[1], last_name=raw[2],
                        role=raw[3], is_approved=raw[4], storage_used=raw[5],
                        space_id=raw[6],
                    ).value
            except OperationalError as e:
                print(f"Error finding user by email: {e}")
        connection.close()
        return result

    def find_account_by_email(self: Self, email: str) -> Account | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT a.id, a.email, a.password, a.created_at, a.is_active,
                       a.reset_token, a.reset_token_expiry, a.user_id
                FROM accounts a WHERE a.email = {email}
            """).format(email=sql.Literal(email))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = Account.create(
                        id=raw[0], email=raw[1], password=raw[2],
                        is_active=raw[4], reset_token=raw[5],
                        reset_token_expiry=str(raw[6]) if raw[6] else None,
                        user_id=raw[7],
                    ).value
            except OperationalError as e:
                print(f"Error finding account: {e}")
        connection.close()
        return result

    def find_account_by_user_id(self: Self, user_id: UUID) -> Account | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT a.id, a.email, a.password, a.created_at, a.is_active,
                       a.reset_token, a.reset_token_expiry, a.user_id
                FROM accounts a WHERE a.user_id = {user_id}
            """).format(user_id=sql.Literal(user_id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = Account.create(
                        id=raw[0], email=raw[1], password=raw[2],
                        is_active=raw[4], reset_token=raw[5],
                        reset_token_expiry=str(raw[6]) if raw[6] else None,
                        user_id=raw[7],
                    ).value
            except OperationalError as e:
                print(f"Error finding account: {e}")
        connection.close()
        return result

    def find_account_by_reset_token(self: Self, token: str) -> Account | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT a.id, a.email, a.password, a.created_at, a.is_active,
                       a.reset_token, a.reset_token_expiry, a.user_id
                FROM accounts a WHERE a.reset_token = {token}
            """).format(token=sql.Literal(token))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = Account.create(
                        id=raw[0], email=raw[1], password=raw[2],
                        is_active=raw[4], reset_token=raw[5],
                        reset_token_expiry=str(raw[6]) if raw[6] else None,
                        user_id=raw[7],
                    ).value
            except OperationalError as e:
                print(f"Error finding account by reset token: {e}")
        connection.close()
        return result

    def find_role_by_id(self: Self, id: UUID) -> Role | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT role FROM users WHERE id = {id}
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = Role(raw[0])
            except OperationalError as e:
                print(f"Error finding role: {e}")
        connection.close()
        return result

    def find_all_by_space(self: Self, space_id: UUID) -> list[User]:
        connection = postgresql_connection()
        result: list[User] = []
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT u.id, u.first_name, u.last_name, u.role, u.is_approved,
                       u.storage_used, u.space_id
                FROM users u WHERE u.space_id = {space_id}
            """).format(space_id=sql.Literal(space_id))
            try:
                cursor.execute(statement)
                for raw in cursor.fetchall():
                    user = User.create(
                        id=raw[0], first_name=raw[1], last_name=raw[2],
                        role=raw[3], is_approved=raw[4], storage_used=raw[5],
                        space_id=raw[6],
                    ).value
                    result.append(user)
            except OperationalError as e:
                print(f"Error finding users: {e}")
        connection.close()
        return result

    def update(self: Self, user: User) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                UPDATE users
                SET first_name = {first_name}, last_name = {last_name},
                    role = {role}, is_approved = {is_approved}, storage_used = {storage_used}
                WHERE id = {id}
            """).format(
                id=sql.Literal(str(user.id)),
                first_name=sql.Literal(user.name.first_name),
                last_name=sql.Literal(user.name.last_name),
                role=sql.Literal(user.role.role_type.value),
                is_approved=sql.Literal(user.is_approved),
                storage_used=sql.Literal(user.storage_used),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error updating user: {e}")
        connection.close()

    def update_account(self: Self, account: Account) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                UPDATE accounts
                SET email = {email}, password = {password}, is_active = {is_active},
                    reset_token = {reset_token}, reset_token_expiry = {reset_token_expiry}
                WHERE id = {id}
            """).format(
                id=sql.Literal(str(account.id)),
                email=sql.Literal(account.email.address),
                password=sql.Literal(account.password.passphrase),
                is_active=sql.Literal(account.is_active),
                reset_token=sql.Literal(account.reset_token),
                reset_token_expiry=sql.Literal(account.reset_token_expiry),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error updating account: {e}")
        connection.close()

    def update_storage_used(self: Self, user_id: UUID, size: int) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                UPDATE users SET storage_used = {size} WHERE id = {id}
            """).format(
                id=sql.Literal(user_id),
                size=sql.Literal(size),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error updating storage: {e}")
        connection.close()

    def remove_by_id(self: Self, id: UUID) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                DELETE FROM users WHERE id = {id}
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error removing user: {e}")
        connection.close()
