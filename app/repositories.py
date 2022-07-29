import logging
from uuid import UUID
from app.models import Image


class ImageRepository:
    def __init__(self):
        self.images = []

    def store_image_data(self, file_path: str, uuid: UUID, client_id: str) -> None:
        self.images.append(Image(file_path=file_path, uuid=str(uuid), client_id=client_id))

    def delete_image(self, uuid: UUID) -> bool:
        try:
            self.images.remove(self.query_images(uuid, 'uuid')[0])
            return True
        except Exception as e:
            logging.log(logging.WARNING, e)
            return False

    def query_images(self, field_value: UUID | str, field_name: str) -> list[Image]:
        return [image for image in self.images if image.dict()[field_name] == str(field_value)]

    def close(self) -> None:
        self.images = []


db = ImageRepository()
