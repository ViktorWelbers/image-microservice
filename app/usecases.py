from uuid import uuid4, UUID

from fastapi import UploadFile

from app.models import Image
from app.repositories import ImageRepository
from app.utils.file_system_utils import FileManagement


class ImageUseCase:
    def __init__(self, repository: ImageRepository):
        self.repository = repository

    def upload(self, file: UploadFile, client_id: str) -> UUID:
        uuid = uuid4()
        file_path = FileManagement.generate_filepath(uuid, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        self.repository.store_image(
            Image(file_path=str(file_path), uuid=str(uuid), client_id=client_id, file_name=file.filename).dict()
        )
        return uuid

    def delete_image_uuid(self, uuid: UUID) -> dict:
        success = self.repository.delete_image(uuid)
        if success:
            FileManagement.remove_file(str(uuid))
        return {'success': success}

    def get_images_for_client_id(self, client_id: str) -> list:
        result = self.repository.query_images('client_id', client_id)
        return [Image(**image) for image in result]

    def get_image_for_uuid(self, uuid: UUID) -> Image | None:
        result = self.repository.query_image('uuid', str(uuid))
        if result:
            return Image(**result)
        else:
            return None

    def download_image_uuid(self, uuid: UUID) -> bytes:
        file_path = self.repository.get_image_file_path(uuid)
        with open(file_path, "rb") as f:
            return f.read()
