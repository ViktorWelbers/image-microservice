from uuid import UUID
from app.utils.dependancies import get_image_use_case
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.models import Image
from app.usecases import ImageUseCase

router = APIRouter(prefix='/images', tags=['images'])


@router.post('/upload/{client_id}', responses={200: {'content': {'text/plain'}}}, tags=['images'])
async def upload_image(client_id: str, file: UploadFile = File(None, description=''),
                       use_case: ImageUseCase = Depends(get_image_use_case)) -> UUID:
    return use_case.upload(file, client_id)


@router.post('/delete/{uuid}', responses={200: {'content': {'application/json'}}}, tags=['images'])
def delete_image(uuid: UUID, use_case: ImageUseCase = Depends(get_image_use_case)) -> JSONResponse:
    return JSONResponse(content=use_case.delete_image_uuid(uuid))


@router.get('/get/{client_id}', response_model=list[Image], tags=['images'])
def get_images_for_client(client_id: str, use_case: ImageUseCase = Depends(get_image_use_case)) -> list[Image]:
    return use_case.get_images_for_client_id(client_id)


@router.get('/get/{uuid}', response_model=Image, tags=['images'])
def get_image_for_uuid(uuid: UUID, use_case: ImageUseCase = Depends(get_image_use_case)) -> Image:
    return use_case.get_image_for_uuid(uuid)
