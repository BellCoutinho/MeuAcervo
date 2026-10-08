from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.entrypoints.rest_api.dependencies import get_current_user
from src.entrypoints.rest_api.schemas.product import (
    RegisterProductRequest, UpdateProductRequest, DeactivateProductRequest,
)
from src.main.factories.product_repository_factory import make_product_repository
from src.main.factories.product_file_repository_factory import make_product_file_repository

router = APIRouter(prefix="/api/product", tags=["product"])


@router.post("", status_code=status.HTTP_201_CREATED)
def register_product(data: RegisterProductRequest, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.register_product import RegisterProduct, RegisterProductData
    use_case = RegisterProduct(make_product_repository())
    result = use_case.perform(RegisterProductData(
        user_id=user["id"],
        space_id=data.space_id,
        name=data.name,
        category=data.category,
        brand=data.brand,
        model=data.model,
        location=data.location,
        purchase_value=data.purchase_value,
        purchase_date=data.purchase_date,
        serial_number=data.serial_number,
        warranty_type=data.warranty_type,
        warranty_expiry=data.warranty_expiry,
        extended_warranty_expiry=data.extended_warranty_expiry,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.get("/search")
def search_products(
    user: dict = Depends(get_current_user),
    space_id: str = Query(...),
    term: str | None = Query(None),
    category: str | None = Query(None),
    warranty_status: str | None = Query(None),
    min_value: float | None = Query(None),
    max_value: float | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    from src.application.use_case.product.get_space_products import GetSpaceProducts, GetSpaceProductsData
    use_case = GetSpaceProducts(make_product_repository())
    result = use_case.perform(GetSpaceProductsData(
        user_id=user["id"],
        space_id=space_id,
        term=term,
        category=category,
        warranty_status=warranty_status,
        min_value=min_value,
        max_value=max_value,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.get("/{product_id}")
def get_product(product_id: str, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.get_product import GetProduct, GetProductData
    use_case = GetProduct(make_product_repository(), make_product_file_repository())
    result = use_case.perform(GetProductData(user_id=user["id"], product_id=product_id))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.put("/{product_id}")
def update_product(product_id: str, data: UpdateProductRequest, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.update_product import UpdateProduct, UpdateProductData
    use_case = UpdateProduct(make_product_repository())
    result = use_case.perform(UpdateProductData(
        user_id=user["id"],
        product_id=product_id,
        name=data.name,
        category=data.category,
        brand=data.brand,
        model=data.model,
        location=data.location,
        purchase_value=data.purchase_value,
        purchase_date=data.purchase_date,
        serial_number=data.serial_number,
        warranty_type=data.warranty_type,
        warranty_expiry=data.warranty_expiry,
        extended_warranty_expiry=data.extended_warranty_expiry,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Produto atualizado com sucesso"}


@router.patch("/{product_id}/deactivate")
def deactivate_product(product_id: str, data: DeactivateProductRequest, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.delete_product import DeleteProduct, DeleteProductData
    use_case = DeleteProduct(make_product_repository())
    result = use_case.perform(DeleteProductData(
        user_id=user["id"],
        product_id=product_id,
        reason=data.reason,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Produto desativado com sucesso"}
