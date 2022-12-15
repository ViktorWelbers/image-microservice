import io
from abc import ABC
from uuid import uuid4, UUID

from PIL import Image
from fastapi import UploadFile

from app.file_system import AzureFileSystem
from app.models import ImageDocument
from app.repositories import ImageRepository


class ImageUseCase(ABC):
    def __init__(self, repository: ImageRepository, file_system: AzureFileSystem):
        self.repository = repository
        self.file_system = file_system


class ImageUploadUseCase(ImageUseCase):
    image_size = (512, 512)

    def upload(
        self, file: UploadFile, client_id: str, processed: bool
    ) -> dict[str, str]:
        uuid = uuid4()
        bytes_io = io.BytesIO(file.file.read())
        image = Image.open(bytes_io)
        image.thumbnail(ImageUploadUseCase.image_size, Image.ANTIALIAS)
        cropped_image_bytes = io.BytesIO()
        image.save(cropped_image_bytes, format=image.format)
        cropped_image_bytes.seek(0)
        self.file_system.upload_file(
            file_name=file.filename,
            file_content=cropped_image_bytes.read(),
            client_id=client_id,
            uuid=uuid,
        )
        self.repository.put_image(
            ImageDocument(
                file_path=client_id + "/" + str(uuid),
                uuid=str(uuid),
                client_id=client_id,
                file_name=file.filename,
                content_type=file.content_type,
                tags={"processed": processed},
            ).dict()
        )
        return {"uuid": str(uuid)}


class ImageDeleteUseCase(ImageUseCase):
    def delete_image_uuid(self, uuid: UUID) -> dict[str, str]:
        success = self.repository.delete_image(uuid)
        if success:
            self.file_system.remove_file(str(uuid))
        return {"Result": "OK" if success else "NOT_FOUND"}


class ImageRetrievalUseCase(ImageUseCase):
    def get_images_for_client_id(self, client_id: str) -> list[ImageDocument]:
        result = self.repository.query_images("client_id", client_id)
        return [ImageDocument(**image) for image in result]

    def get_image_for_uuid(self, uuid: UUID) -> ImageDocument | None:
        result = self.repository.query_image("uuid", str(uuid))
        if result:
            return ImageDocument(**result)
        return None
