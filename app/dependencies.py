from fastapi import Depends
from pymongo import MongoClient

from app.file_system import AzureFileSystem
from app.handlers import DownloadHandler, UploadHandler, DeleteHandler, MetadataHandler
from app.repositories import ImageRepository
from app.settings import get_settings
from app.usecases import (
    ImageUploadUseCase,
    ImageDeleteUseCase,
    ImageDownloadUseCase,
    ImageMetadataUseCase,
)


async def get_mongo_client() -> MongoClient:
    mongo_client = MongoClient(get_settings().mongo_uri)
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
    return ImageRepository(
        mongo_client,
        get_settings().mongo_db_name,
        get_settings().mongo_collection,
    )


async def get_upload_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageUploadUseCase:
    return ImageUploadUseCase(repository, file_system)


async def get_delete_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageDeleteUseCase:
    return ImageDeleteUseCase(repository, file_system)


async def get_download_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageDownloadUseCase:
    return ImageDownloadUseCase(repository, file_system)


async def get_client_metadata_use_case(
    repository: ImageRepository = Depends(get_repository),
    file_system: AzureFileSystem = Depends(get_azure_file_system),
) -> ImageMetadataUseCase:
    return ImageMetadataUseCase(repository, file_system)


async def get_upload_handler(
    use_case: ImageUploadUseCase = Depends(get_upload_use_case),
) -> UploadHandler:
    return UploadHandler(use_case)


async def get_delete_handler(
    use_case: ImageDeleteUseCase = Depends(get_delete_use_case),
) -> DeleteHandler:
    return DeleteHandler(use_case)


async def get_metadata_handler(
    use_case: ImageMetadataUseCase = Depends(get_client_metadata_use_case),
) -> MetadataHandler:
    return MetadataHandler(use_case)


async def get_download_handler(
    use_case: ImageDownloadUseCase = Depends(get_download_use_case),
) -> DownloadHandler:
    return DownloadHandler(use_case)
