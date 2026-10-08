import pytest
from src.domain.value_objects import (
    Email, Name, UniqueId, Role, SpaceName, Address,
    ProductName, Category, Brand, Model, Location,
    PurchaseValue, SerialNumber, FileTypeVO, FileSize,
)


class TestEmail:
    def test_valid_email(self):
        result = Email.create(address="test@example.com")
        assert result.is_success
        assert result.value.address == "test@example.com"

    def test_invalid_email_no_at(self):
        result = Email.create(address="testexample.com")
        assert result.is_failure

    def test_invalid_email_short_local(self):
        result = Email.create(address="ab@example.com")
        assert result.is_failure

    def test_missing_email(self):
        result = Email.validate(address=None)
        assert result.is_failure


class TestName:
    def test_valid_name(self):
        result = Name.create(first_name="João", last_name="Silva")
        assert result.is_success
        assert result.value.full_name == "João Silva"

    def test_missing_first_name(self):
        result = Name.validate(first_name=None, last_name="Silva")
        assert result.is_failure

    def test_missing_last_name(self):
        result = Name.validate(first_name="João", last_name=None)
        assert result.is_failure


class TestUniqueId:
    def test_auto_generate(self):
        result = UniqueId.create()
        assert result.is_success
        assert result.value.identifier is not None

    def test_valid_uuid(self):
        result = UniqueId.create(id="550e8400-e29b-41d4-a716-446655440000")
        assert result.is_success

    def test_invalid_uuid(self):
        result = UniqueId.create(id="not-a-uuid")
        assert result.is_failure


class TestRole:
    def test_admin(self):
        result = Role.create(role_type="admin")
        assert result.is_success
        assert result.value.role_type.value == "admin"

    def test_user(self):
        result = Role.create(role_type="user")
        assert result.is_success

    def test_invalid_role(self):
        result = Role.create(role_type="superadmin")
        assert result.is_failure


class TestSpaceName:
    def test_valid(self):
        result = SpaceName.create(name="Minha Casa")
        assert result.is_success

    def test_too_short(self):
        result = SpaceName.create(name="AB")
        assert result.is_failure


class TestAddress:
    def test_valid(self):
        result = Address.create(address="Rua das Flores, 123 - Centro")
        assert result.is_success

    def test_too_short(self):
        result = Address.create(address="Rua")
        assert result.is_failure


class TestProductName:
    def test_valid(self):
        result = ProductName.create(name="Televisão Samsung")
        assert result.is_success

    def test_too_short(self):
        result = ProductName.create(name="A")
        assert result.is_failure


class TestCategory:
    def test_valid_eletronico(self):
        result = Category.create(category="eletronico")
        assert result.is_success

    def test_invalid_category(self):
        result = Category.create(category="invalido")
        assert result.is_failure


class TestBrand:
    def test_valid(self):
        result = Brand.create(brand="Samsung")
        assert result.is_success


class TestModel:
    def test_valid(self):
        result = Model.create(model="QN55Q60R")
        assert result.is_success


class TestLocation:
    def test_valid(self):
        result = Location.create(location="Sala de estar")
        assert result.is_success


class TestPurchaseValue:
    def test_valid(self):
        result = PurchaseValue.create(value=2500.00)
        assert result.is_success

    def test_zero(self):
        result = PurchaseValue.create(value=0)
        assert result.is_failure

    def test_negative(self):
        result = PurchaseValue.create(value=-100)
        assert result.is_failure


class TestSerialNumber:
    def test_valid(self):
        result = SerialNumber.create(serial_number="SN12345678")
        assert result.is_success
        assert result.value.serial_number == "SN12345678"

    def test_none(self):
        result = SerialNumber.create(serial_number=None)
        assert result.is_success
        assert result.value.serial_number is None


class TestFileTypeVO:
    def test_valid_nf(self):
        result = FileTypeVO.create(file_type="nf")
        assert result.is_success

    def test_valid_photo(self):
        result = FileTypeVO.create(file_type="photo")
        assert result.is_success

    def test_invalid(self):
        result = FileTypeVO.create(file_type="docx")
        assert result.is_failure


class TestFileSize:
    def test_valid(self):
        result = FileSize.create(size=1024)
        assert result.is_success

    def test_zero(self):
        result = FileSize.create(size=0)
        assert result.is_failure
