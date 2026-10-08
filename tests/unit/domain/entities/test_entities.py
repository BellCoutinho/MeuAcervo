import pytest
from unittest.mock import MagicMock, patch
from src.domain.entities import Space, User, Account, Product, ProductFile
from src.domain.value_objects import (
    SpaceName, Address, UtilityUnitNumber, Name, Role,
    Email, HashedPassword, ProductName, Category, Brand,
    Model, Location, PurchaseValue,
)


class TestSpace:
    def test_create_valid_space(self):
        result = Space.create(
            name="Minha Casa",
            address="Rua das Flores, 123",
            utility_unit_number="12345678",
        )
        assert result.is_success
        assert result.value.name.name == "Minha Casa"

    def test_space_equality(self):
        space1 = Space.create(
            name="Casa", address="Rua A, 1", utility_unit_number="001",
        ).value
        space2 = Space.create(
            name="Casa", address="Rua A, 1", utility_unit_number="001",
        ).value
        assert space1 != space2


class TestUser:
    def test_create_valid_user(self):
        result = User.create(
            first_name="João",
            last_name="Silva",
            role="admin",
            is_approved=True,
        )
        assert result.is_success
        assert result.value.name.first_name == "João"
        assert result.value.role.role_type.value == "admin"

    def test_user_default_role(self):
        result = User.create(first_name="Maria", last_name="Santos")
        assert result.is_success
        assert result.value.role.role_type.value == "user"


class TestProduct:
    def test_create_valid_product(self):
        result = Product.create(
            name="Televisão",
            category="eletronico",
            brand="Samsung",
            model="QN55Q60R",
            location="Sala",
            purchase_value=2500.00,
            serial_number="SN123",
        )
        assert result.is_success
        assert result.value.name.name == "Televisão"
        assert result.value.purchase_value.value == 2500.00

    def test_product_warranty_status_no_warranty(self):
        result = Product.create(
            name="Notebook",
            category="eletronico",
            brand="Dell",
            model="Inspiron",
            location="Escritório",
            purchase_value=3000.00,
        )
        assert result.is_success
        assert result.value.warranty_status == "Expirada"

    def test_product_invalid_category(self):
        result = Product.create(
            name="TV",
            category="invalido",
            brand="Samsung",
            model="X",
            location="Sala",
            purchase_value=1000,
        )
        assert result.is_failure
