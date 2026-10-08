import pytest
from unittest.mock import MagicMock
from src.application.use_case.product.register_product import RegisterProduct, RegisterProductData
from src.application.use_case.product.delete_product import DeleteProduct, DeleteProductData
from src.application.use_case.product.update_product import UpdateProduct, UpdateProductData
from src.application.use_case.product.get_product import GetProduct, GetProductData
from src.application.use_case.product.get_space_products import GetSpaceProducts, GetSpaceProductsData
from src.domain.entities import Product


class TestRegisterProduct:
    def setup_method(self):
        self.product_repo = MagicMock()
        self.use_case = RegisterProduct(self.product_repo)

    def test_register_success(self):
        result = self.use_case.perform(RegisterProductData(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            space_id="550e8400-e29b-41d4-a716-446655440001",
            name="Televisão Samsung",
            category="eletronico",
            brand="Samsung",
            model="QN55Q60R",
            location="Sala de estar",
            purchase_value=2500.00,
            serial_number="SN123456",
        ))
        assert result.is_success
        self.product_repo.add.assert_called_once()

    def test_register_invalid_category(self):
        result = self.use_case.perform(RegisterProductData(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            space_id="550e8400-e29b-41d4-a716-446655440001",
            name="TV",
            category="invalido",
            brand="Samsung",
            model="X",
            location="Sala",
            purchase_value=1000,
        ))
        assert result.is_failure


class TestDeleteProduct:
    def setup_method(self):
        self.product_repo = MagicMock()
        self.use_case = DeleteProduct(self.product_repo)

    def test_deactivate_success(self):
        mock_product = MagicMock()
        self.product_repo.find_by_id.return_value = mock_product

        result = self.use_case.perform(DeleteProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            reason="broken",
        ))
        assert result.is_success
        self.product_repo.update_status.assert_called_once()

    def test_invalid_reason(self):
        result = self.use_case.perform(DeleteProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            reason="invalid_reason",
        ))
        assert result.is_failure


class TestUpdateProduct:
    def setup_method(self):
        self.product_repo = MagicMock()
        self.use_case = UpdateProduct(self.product_repo)

    def test_update_name_success(self):
        mock_product = MagicMock()
        self.product_repo.find_by_id.return_value = mock_product

        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            name="Novo Nome",
        ))
        assert result.is_success
        self.product_repo.update.assert_called_once()

    def test_update_product_not_found(self):
        self.product_repo.find_by_id.return_value = None

        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            name="Novo Nome",
        ))
        assert result.is_failure

    def test_update_invalid_product_id(self):
        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="not-a-uuid",
            name="Novo Nome",
        ))
        assert result.is_failure

    def test_update_category_success(self):
        mock_product = MagicMock()
        self.product_repo.find_by_id.return_value = mock_product

        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            category="moveis",
        ))
        assert result.is_success

    def test_update_invalid_category(self):
        mock_product = MagicMock()
        self.product_repo.find_by_id.return_value = mock_product

        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            category="invalido",
        ))
        assert result.is_failure

    def test_update_purchase_value(self):
        mock_product = MagicMock()
        self.product_repo.find_by_id.return_value = mock_product

        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            purchase_value=3000.00,
        ))
        assert result.is_success

    def test_update_serial_number(self):
        mock_product = MagicMock()
        self.product_repo.find_by_id.return_value = mock_product

        result = self.use_case.perform(UpdateProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
            serial_number="SN789",
        ))
        assert result.is_success


class TestGetProduct:
    def setup_method(self):
        self.product_repo = MagicMock()
        self.file_repo = MagicMock()
        self.use_case = GetProduct(self.product_repo, self.file_repo)

    def test_get_product_success(self):
        mock_product = MagicMock()
        mock_product.id = "product-123"
        mock_product.name.name = "TV Samsung"
        mock_product.category.category.value = "eletronico"
        mock_product.brand.brand = "Samsung"
        mock_product.model.model = "QN55Q60R"
        mock_product.location.location = "Sala"
        mock_product.purchase_value.value = 2500.00
        mock_product.serial_number.serial_number = "SN123"
        mock_product.warranty_type = "manufacturer"
        mock_product.warranty_status = "valid"
        mock_product.status = "active"

        self.product_repo.find_by_id.return_value = mock_product
        self.file_repo.find_by_product_id.return_value = []

        result = self.use_case.perform(GetProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert result.value["name"] == "TV Samsung"

    def test_get_product_not_found(self):
        self.product_repo.find_by_id.return_value = None

        result = self.use_case.perform(GetProductData(
            user_id="user-123",
            product_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_failure

    def test_get_product_invalid_id(self):
        result = self.use_case.perform(GetProductData(
            user_id="user-123",
            product_id="not-a-uuid",
        ))
        assert result.is_failure


class TestGetSpaceProducts:
    def setup_method(self):
        self.product_repo = MagicMock()
        self.use_case = GetSpaceProducts(self.product_repo)

    def test_search_products_success(self):
        mock_product = MagicMock()
        mock_product.id = "product-123"
        mock_product.name.name = "TV Samsung"
        mock_product.category.category.value = "eletronico"
        mock_product.brand.brand = "Samsung"
        mock_product.model.model = "QN55Q60R"
        mock_product.purchase_value.value = 2500.00
        mock_product.warranty_status = "valid"
        mock_product.status = "active"

        self.product_repo.search.return_value = [mock_product]

        result = self.use_case.perform(GetSpaceProductsData(
            user_id="user-123",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert len(result.value) == 1

    def test_search_invalid_space_id(self):
        result = self.use_case.perform(GetSpaceProductsData(
            user_id="user-123",
            space_id="not-a-uuid",
        ))
        assert result.is_failure

    def test_search_empty_results(self):
        self.product_repo.search.return_value = []

        result = self.use_case.perform(GetSpaceProductsData(
            user_id="user-123",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert len(result.value) == 0

    def test_search_with_filters(self):
        self.product_repo.search.return_value = []

        result = self.use_case.perform(GetSpaceProductsData(
            user_id="user-123",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            term="samsung",
            category="eletronico",
            min_value=1000,
            max_value=5000,
        ))
        assert result.is_success
