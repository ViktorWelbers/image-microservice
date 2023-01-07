from datetime import datetime
import io
from abc import ABC, abstractmethod
from uuid import uuid4, UUID

from PIL import Image
from fastapi import UploadFile

from app.file_system import AzureFileSystem
from app.schemas import ImageDocument
from app.repositories import ImageRepository


class ImageUseCase(ABC):
    def __init__(self, repository: ImageRepository, file_system: AzureFileSystem):
        self.repository = repository
        self.file_system = file_system

    @abstractmethod
    def execute(
        self, *args, **kwargs
    ) -> dict[str, str] | list[dict] | tuple[bytes, str] | bool:
        raise NotImplementedError


class ImageUploadUseCase(ImageUseCase):
    image_size = (768, 768)

    def execute(
        self, file: UploadFile, body: dict, processed: bool, origin_uuid: None | str
    ) -> dict[str, str]:
        client_id = body["client_id"]
        uuid = uuid4()
        bytes_io = io.BytesIO(file.file.read())
        image = Image.open(bytes_io)
        image.thumbnail(ImageUploadUseCase.image_size, Image.ANTIALIAS)
        cropped_image_bytes = io.BytesIO()
        image.save(cropped_image_bytes, format=image.format)
        cropped_image_bytes.seek(0)
        self.repository.put_image(
            ImageDocument(
                file_path=client_id + "/" + str(uuid),
                uuid=str(uuid),
                client_id=client_id,
                file_name=file.filename,
                content_type=file.content_type,
                tags={
                    "origin_uuid": origin_uuid,
                    "processed": processed,
                    "timestamp": datetime.now().isoformat(),
                },
            ).dict()
        )
        self.file_system.upload_file(
            file_name=file.filename,
            file_content=cropped_image_bytes.read(),
            client_id=client_id,
            uuid=uuid,
        )
        return {"uuid": str(uuid)}


class ImageDeleteUseCase(ImageUseCase):
    def execute(self, uuid: UUID) -> bool:
        document = self.repository.query_image(field_key="uuid", field_value=str(uuid))
        if not document:
            return False
        self.file_system.delete_file(
            file_name=document["file_name"], file_path=document["file_path"]
        )
        self.repository.delete_image(uuid)
        return True


class ImageMetadataUseCase(ImageUseCase):
    def execute(self, client_id: str) -> list[dict]:
        return self.repository.query_images("client_id", client_id)


class ImageDownloadUseCase(ImageUseCase):
    def execute(self, uuid: UUID) -> tuple[bytes, str] | tuple[None, None]:
        document = self.repository.query_image(field_key="uuid", field_value=str(uuid))
        if not document:
            return None, None
        return self.file_system.download_file(
            file_name=document["file_name"], file_path=document["file_path"]
        )
