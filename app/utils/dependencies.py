from fastapi import Depends
from pymongo import MongoClient

from app.repositories import ImageRepository
from app.usecases import ImageUseCase
from app.utils.configuration import get_settings


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


async def get_use_case(repository: ImageRepository = Depends(get_repository)) -> ImageUseCase:
    return ImageUseCase(repository)
