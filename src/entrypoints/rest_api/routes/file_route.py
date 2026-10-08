import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse

from src.entrypoints.rest_api.dependencies import get_current_user
from src.main.factories.product_repository_factory import make_product_repository
from src.main.factories.product_file_repository_factory import make_product_file_repository
from src.main.factories.user_repository_factory import make_user_repository
from src.main.factories.space_repository_factory import make_space_repository
from src.main.factories.file_storage_factory import make_file_storage

router = APIRouter(prefix="/api/file", tags=["file"])


@router.post("/upload/{product_id}", status_code=status.HTTP_201_CREATED)
async def upload_file(
    product_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    content = await file.read()
    file_size = len(content)

    max_size = int(os.environ.get('MAX_FILE_SIZE_MB', '50')) * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=413, detail="Arquivo excede o tamanho máximo")

    from src.application.use_case.product.upload_file import UploadFile as UploadFileUC, UploadFileData
    use_case = UploadFileUC(
        make_product_file_repository(),
        make_product_repository(),
        make_user_repository(),
        make_space_repository(),
        make_file_storage(),
    )
    result = use_case.perform(UploadFileData(
        user_id=user["id"],
        product_id=product_id,
        file_name=file.filename or "unknown",
        file_content=content,
        file_type=_guess_file_type(file.filename or ""),
        file_size=file_size,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.delete("/{file_id}")
def delete_file(file_id: str, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.delete_file import DeleteFile, DeleteFileData
    use_case = DeleteFile(
        make_product_file_repository(),
        make_user_repository(),
        make_file_storage(),
    )
    result = use_case.perform(DeleteFileData(user_id=user["id"], file_id=file_id))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Arquivo removido com sucesso"}


@router.get("/product/{product_id}")
def get_product_files(product_id: str, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.get_product_files import GetProductFiles, GetProductFilesData
    use_case = GetProductFiles(make_product_file_repository(), make_product_repository())
    result = use_case.perform(GetProductFilesData(user_id=user["id"], product_id=product_id))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.get("/download/{file_id}")
def download_file(file_id: str, user: dict = Depends(get_current_user)):
    from src.application.use_case.product.get_product_files import GetProductFiles, GetProductFilesData
    repo = make_product_file_repository()
    product_file = repo.find_by_id(file_id)
    if not product_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado")
    file_path = product_file.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado no disco")
    return FileResponse(
        path=file_path,
        filename=product_file.file_name,
        media_type="application/octet-stream",
    )


def _guess_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return "nf"
    if ext in ("jpg", "jpeg", "png", "gif", "bmp"):
        return "photo"
    if ext in ("mp4", "avi", "mov", "mkv"):
        return "video"
    if ext in ("doc", "docx", "txt"):
        return "contract"
    return "other"
