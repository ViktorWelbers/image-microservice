from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse

from app.dependencies import get_upload_use_case, get_delete_use_case, get_retrieval_use_case
from app.entities import serve_file
from app.models import ImageDocument
from app.usecases import ImageRetrievalUseCase, ImageUploadUseCase, ImageDeleteUseCase

router = APIRouter(prefix='/images', tags=['images'])


@router.post('/upload/{client_id}', response_class=JSONResponse, response_model=dict, tags=['images'])
async def upload_image(client_id: str, file: UploadFile = File(description='', media_type='image/*'),
                       use_case: ImageUploadUseCase = Depends(get_upload_use_case)) -> JSONResponse:
    return JSONResponse(content=use_case.upload(file, client_id))


@router.post('/delete/', response_class=JSONResponse, response_model=dict, tags=['images'])
def delete_image(uuid: UUID, use_case: ImageDeleteUseCase = Depends(get_delete_use_case)) -> JSONResponse:
    return JSONResponse(content=use_case.delete_image_uuid(uuid))


@router.get('/get_images', response_model=list[ImageDocument], response_class=JSONResponse, tags=['images'])
def get_images_for_client_id(client_id: str,
                             use_case: ImageRetrievalUseCase = Depends(get_retrieval_use_case)) -> list[ImageDocument]:
    return use_case.get_images_for_client_id(client_id)


@router.get('/get_image/', response_model=ImageDocument, response_class=JSONResponse, tags=['images'])
def get_image_for_uuid(uuid: UUID, use_case: ImageRetrievalUseCase = Depends(get_retrieval_use_case)) -> ImageDocument:
    return use_case.get_image_for_uuid(uuid)


@router.get('/download/{uuid}', response_class=FileResponse, tags=['images'])
def download_image(uuid: UUID, use_case: ImageRetrievalUseCase = Depends(get_retrieval_use_case)) -> FileResponse:
    return serve_file(use_case.get_image_for_uuid(uuid))
