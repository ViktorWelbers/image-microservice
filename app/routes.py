from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse
from starlette.responses import Response

from app.dependencies import (
    get_download_handler,
    get_upload_handler,
    get_delete_handler,
    get_metadata_handler,
)
from app.handlers import DownloadHandler, MetadataHandler, DeleteHandler, UploadHandler
from app.schemas import ImageDocument

router = APIRouter(prefix="/images")


@router.post(
    "/upload/{client_id}",
    response_class=JSONResponse,
    response_model=dict,
    tags=["upload"],
)
async def upload_image(
    client_id: str,
    processed: bool = False,
    file: UploadFile = File(description="", media_type="image/*"),
    handler: UploadHandler = Depends(get_upload_handler),
) -> JSONResponse:
    return handler.handle(file, client_id, processed)


@router.post(
    "/delete/{uuid}",
    response_class=JSONResponse,
    response_model=dict,
    tags=["delete"],
)
def delete_image(
    uuid: UUID, handler: DeleteHandler = Depends(get_delete_handler)
) -> JSONResponse:
    return handler.handle(uuid)


@router.get(
    "/images_metadata/{client_id}",
    response_model=list[ImageDocument],
    response_class=JSONResponse,
    tags=["metadata"],
)
def get_metadata_images_for_client_id(
    client_id: str, handler: MetadataHandler = Depends(get_metadata_handler)
) -> list[ImageDocument]:
    return handler.handle(client_id)


@router.get(
    "/download/{uuid}",
    response_class=FileResponse,
    tags=["download"],
)
def download_image(
    uuid: UUID, handler: DownloadHandler = Depends(get_download_handler)
) -> Response:
    return handler.handle(uuid)
