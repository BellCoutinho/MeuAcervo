from __future__ import annotations

from typing import Self
from uuid import UUID

from psycopg import OperationalError, sql

from src.domain.entities import Product
from src.domain.repositories import ProductRepository
from src.infrastructure.databases.postgresql.connection import postgresql_connection


class ProductPostgreSQLRepository(ProductRepository):

    def add(self: Self, product: Product) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                INSERT INTO product(id, name, category, brand, model, location,
                    purchase_date, purchase_value, serial_number, warranty_type,
                    warranty_expiry, extended_warranty_expiry, status, status_reason,
                    user_id, space_id, created_at)
                VALUES({id}, {name}, {category}, {brand}, {model}, {location},
                    {purchase_date}, {purchase_value}, {serial_number}, {warranty_type},
                    {warranty_expiry}, {ext_warranty}, {status}, {status_reason},
                    {user_id}, {space_id}, {created_at})
            """).format(
                id=sql.Literal(str(product.id)),
                name=sql.Literal(product.name.name),
                category=sql.Literal(product.category.category.value),
                brand=sql.Literal(product.brand.brand),
                model=sql.Literal(product.model.model),
                location=sql.Literal(product.location.location),
                purchase_date=sql.Literal(product.purchase_date.value if product.purchase_date else None),
                purchase_value=sql.Literal(product.purchase_value.value),
                serial_number=sql.Literal(product.serial_number.serial_number),
                warranty_type=sql.Literal(product.warranty_type),
                warranty_expiry=sql.Literal(product.warranty_expiry.value if product.warranty_expiry and product.warranty_expiry.value else None),
                ext_warranty=sql.Literal(product.extended_warranty_expiry.value if product.extended_warranty_expiry and product.extended_warranty_expiry.value else None),
                status=sql.Literal(product.status),
                status_reason=sql.Literal(product.status_reason),
                user_id=sql.Literal(str(product.user_id)) if product.user_id else sql.Literal(None),
                space_id=sql.Literal(str(product.space_id)) if product.space_id else sql.Literal(None),
                created_at=sql.Literal(product.created_at.value),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error adding product: {e}")
        connection.close()

    def find_by_id(self: Self, id: UUID) -> Product | None:
        connection = postgresql_connection()
        result = None
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT id, name, category, brand, model, location,
                    purchase_date, purchase_value, serial_number, warranty_type,
                    warranty_expiry, extended_warranty_expiry, status, status_reason,
                    user_id, space_id, created_at
                FROM product WHERE id = {id}
            """).format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                raw = cursor.fetchone()
                if raw:
                    result = self._map_row_to_product(raw)
            except OperationalError as e:
                print(f"Error finding product: {e}")
        connection.close()
        return result

    def find_by_space_id(self: Self, space_id: UUID) -> list[Product]:
        connection = postgresql_connection()
        result: list[Product] = []
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                SELECT id, name, category, brand, model, location,
                    purchase_date, purchase_value, serial_number, warranty_type,
                    warranty_expiry, extended_warranty_expiry, status, status_reason,
                    user_id, space_id, created_at
                FROM product WHERE space_id = {space_id} AND status = 'active'
            """).format(space_id=sql.Literal(space_id))
            try:
                cursor.execute(statement)
                for raw in cursor.fetchall():
                    result.append(self._map_row_to_product(raw))
            except OperationalError as e:
                print(f"Error finding products: {e}")
        connection.close()
        return result

    def search(
        self: Self,
        space_id: UUID,
        term: str | None = None,
        category: str | None = None,
        warranty_status: str | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> list[Product]:
        connection = postgresql_connection()
        result: list[Product] = []
        conditions = ["space_id = {space_id}", "status = 'active'"]
        params = {"space_id": space_id}

        if term:
            conditions.append(
                "(name ILIKE {term} OR brand ILIKE {term} OR model ILIKE {term} OR serial_number ILIKE {term})"
            )
            params["term"] = f"%{term}%"
        if category:
            conditions.append("category = {category}")
            params["category"] = category
        if min_value is not None:
            conditions.append("purchase_value >= {min_value}")
            params["min_value"] = min_value
        if max_value is not None:
            conditions.append("purchase_value <= {max_value}")
            params["max_value"] = max_value

        where_clause = " AND ".join(conditions)

        safe_sort_order = "ASC" if sort_order.upper() == "ASC" else "DESC"
        if sort_by == "purchase_value":
            order = f"purchase_value {safe_sort_order}"
        else:
            order = f"created_at {safe_sort_order}"

        query = f"""
            SELECT id, name, category, brand, model, location,
                purchase_date, purchase_value, serial_number, warranty_type,
                warranty_expiry, extended_warranty_expiry, status, status_reason,
                user_id, space_id, created_at
            FROM product WHERE {where_clause} ORDER BY {order}
            LIMIT {int(limit)} OFFSET {int(offset)}
        """

        with connection.cursor() as cursor:
            try:
                formatted = sql.SQL(query).format(**{k: sql.Literal(v) for k, v in params.items()})
                cursor.execute(formatted)
                for raw in cursor.fetchall():
                    result.append(self._map_row_to_product(raw))
            except OperationalError as e:
                print(f"Error searching products: {e}")
        connection.close()

        if warranty_status:
            result = [p for p in result if p.warranty_status.lower().startswith(warranty_status.lower())]

        return result

    def update(self: Self, product: Product) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                UPDATE product
                SET name = {name}, category = {category}, brand = {brand},
                    model = {model}, location = {location},
                    purchase_date = {purchase_date}, purchase_value = {purchase_value},
                    serial_number = {serial_number}, warranty_type = {warranty_type},
                    warranty_expiry = {warranty_expiry},
                    extended_warranty_expiry = {ext_warranty}
                WHERE id = {id}
            """).format(
                id=sql.Literal(str(product.id)),
                name=sql.Literal(product.name.name),
                category=sql.Literal(product.category.category.value),
                brand=sql.Literal(product.brand.brand),
                model=sql.Literal(product.model.model),
                location=sql.Literal(product.location.location),
                purchase_date=sql.Literal(product.purchase_date.value if product.purchase_date else None),
                purchase_value=sql.Literal(product.purchase_value.value),
                serial_number=sql.Literal(product.serial_number.serial_number),
                warranty_type=sql.Literal(product.warranty_type),
                warranty_expiry=sql.Literal(product.warranty_expiry.value if product.warranty_expiry and product.warranty_expiry.value else None),
                ext_warranty=sql.Literal(product.extended_warranty_expiry.value if product.extended_warranty_expiry and product.extended_warranty_expiry.value else None),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error updating product: {e}")
        connection.close()

    def update_status(self: Self, id: UUID, status: str, reason: str | None) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("""
                UPDATE product SET status = {status}, status_reason = {reason} WHERE id = {id}
            """).format(
                id=sql.Literal(id),
                status=sql.Literal(status),
                reason=sql.Literal(reason),
            )
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error updating status: {e}")
        connection.close()

    def remove_by_id(self: Self, id: UUID) -> None:
        connection = postgresql_connection()
        with connection.cursor() as cursor:
            statement = sql.SQL("DELETE FROM product WHERE id = {id}").format(id=sql.Literal(id))
            try:
                cursor.execute(statement)
                connection.commit()
            except OperationalError as e:
                print(f"Error removing product: {e}")
        connection.close()

    def _map_row_to_product(self, raw: tuple) -> Product:
        from src.domain.value_objects import (
            Brand, Category, Date, Location, Model, ProductName,
            PurchaseValue, SerialNumber, WarrantyDate,
        )
        return Product.create(
            id=raw[0], name=raw[1], category=raw[2], brand=raw[3],
            model=raw[4], location=raw[5],
            purchase_date=str(raw[6]) if raw[6] else None,
            purchase_value=float(raw[7]),
            serial_number=raw[8],
            warranty_type=raw[9],
            warranty_expiry=str(raw[10]) if raw[10] else None,
            extended_warranty_expiry=str(raw[11]) if raw[11] else None,
            status=raw[12],
            status_reason=raw[13],
            user_id=raw[14],
            space_id=raw[15],
        ).value
