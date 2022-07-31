from abc import ABC
from pathlib import Path
from uuid import uuid4, UUID

from PIL import Image
from PIL.ExifTags import TAGS
from fastapi import UploadFile

from app.entities import FileManagement
from app.models import ImageDocument
from app.repositories import ImageRepository


class ImageUseCase(ABC):
    def __init__(self, repository: ImageRepository, file_management: FileManagement):
        self.repository = repository
        self.file_management = file_management


class ImageUploadUseCase(ImageUseCase):

    def _store_image_in_filesystem(self, file: UploadFile, uuid: UUID) -> Path:
        file_path = self.file_management.generate_file(uuid, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return file_path

    @staticmethod
    def _extract_meta_data_from_image(file_path: Path) -> dict[str, str]:
        meta_data = Image.open(file_path)
        data = {str(TAGS[k]): str(v) for k, v in meta_data.getexif().items() if k in TAGS}
        meta_data.close()
        return data

    def upload(self, file: UploadFile, client_id: str) -> dict[str, str]:
        uuid = uuid4()
        file_path = self._store_image_in_filesystem(file, uuid)
        self.repository.put_image(
            ImageDocument(file_path=str(file_path),
                          uuid=str(uuid),
                          client_id=client_id,
                          file_name=file.filename,
                          content_type=file.content_type,
                          tags=self._extract_meta_data_from_image(file_path)
                          ).dict()
        )
        return {'uuid': str(uuid)}


class ImageDeleteUseCase(ImageUseCase):
    def delete_image_uuid(self, uuid: UUID) -> dict[str, str]:
        success = self.repository.delete_image(uuid)
        if success:
            self.file_management.remove_file(str(uuid))
        return {'Result': 'OK' if success else 'NOT_FOUND'}


class ImageRetrievalUseCase(ImageUseCase):
    def get_images_for_client_id(self, client_id: str) -> list[ImageDocument]:
        result = self.repository.query_images('client_id', client_id)
        return [ImageDocument(**image) for image in result]

    def get_image_for_uuid(self, uuid: UUID) -> ImageDocument | None:
        result = self.repository.query_image('uuid', str(uuid))
        if result:
            return ImageDocument(**result)
        return None
