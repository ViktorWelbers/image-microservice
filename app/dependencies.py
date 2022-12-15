from fastapi import Depends
from pymongo import MongoClient

from app.configuration import get_settings
from app.file_system import AzureFileSystem
from app.repositories import ImageRepository
from app.usecases import (
    ImageUseCase,
    ImageUploadUseCase,
    ImageDeleteUseCase,
    ImageRetrievalUseCase,
)


async def get_mongo_client() -> MongoClient:
    mongo_client = MongoClient(
        get_settings().mongo_url,
        username=get_settings().mongo_user,
        password=get_settings().mongo_password,
    )
    try:
        yield mongo_client
    finally:
        mongo_client.close()


def get_azure_file_system() -> AzureFileSystem:
    return AzureFileSystem(
        get_settings().azure_account_name,
        get_settings().azure_account_key,
        get_settings().azure_share_name,
    )


async def get_repository(
    mongo_client: MongoClient = Depends(get_mongo_client),
) -> ImageRepository:
    return ImageRepository(mongo_client)


async def get_upload_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageUseCase:
    return ImageUploadUseCase(
        repository,
        file_system,
    )


async def get_delete_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageUseCase:
    return ImageDeleteUseCase(repository, file_system)


async def get_retrieval_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageUseCase:
    return ImageRetrievalUseCase(repository, file_system)
