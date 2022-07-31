from fastapi import Depends
from pymongo import MongoClient

from app.entities import FileManagement
from app.repositories import ImageRepository
from app.usecases import ImageUseCase, ImageUploadUseCase, ImageDeleteUseCase, ImageRetrievalUseCase
from app.configuration import get_settings


async def get_mongo_client() -> MongoClient:
    mongo_client = MongoClient(get_settings().mongo_url,
                               username=get_settings().mongo_user,
                               password=get_settings().mongo_password)
    try:
        yield mongo_client
    finally:
        mongo_client.close()


async def get_repository(mongo_client: MongoClient = Depends(get_mongo_client)) -> ImageRepository:
    return ImageRepository(mongo_client)


async def get_upload_use_case(repository: ImageRepository = Depends(get_repository)) -> ImageUseCase:
    return ImageUploadUseCase(repository, FileManagement())


async def get_delete_use_case(repository: ImageRepository = Depends(get_repository)) -> ImageUseCase:
    return ImageDeleteUseCase(repository, FileManagement())


async def get_retrieval_use_case(repository: ImageRepository = Depends(get_repository)) -> ImageUseCase:
    return ImageRetrievalUseCase(repository, FileManagement())
