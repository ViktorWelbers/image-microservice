from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse

from app.models import Image
from app.usecases import ImageUseCase
from app.utils.dependencies import get_use_case

router = APIRouter(prefix='/images', tags=['images'])


@router.post('/upload/{client_id}', responses={200: {'content': {'text/plain'}}}, tags=['images'])
async def upload_image(client_id: str, file: UploadFile = File(None, description=''),
                       use_case: ImageUseCase = Depends(get_use_case)) -> UUID:
    return use_case.upload(file, client_id)


@router.post('/delete/', responses={200: {'content': {'application/json'}}}, tags=['images'])
def delete_image(uuid: UUID, use_case: ImageUseCase = Depends(get_use_case)) -> JSONResponse:
    return JSONResponse(content=use_case.delete_image_uuid(uuid))


@router.get('/get_images_data/', response_model=list[Image], responses={200: {'content': {'application/json'}}},
            tags=['images'])
def get_images_for_client_id(client_id: str, use_case: ImageUseCase = Depends(get_use_case)) -> list[Image]:
    return use_case.get_images_for_client_id(client_id)


@router.get('/get_image_data/', response_model=Image, responses={200: {'content': {'application/json'}}},
            tags=['images'])
def get_image_for_uuid(uuid: UUID, use_case: ImageUseCase = Depends(get_use_case)) -> Image:
    return use_case.get_image_for_uuid(uuid)
