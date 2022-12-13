import logging
from uuid import UUID

from bson import ObjectId
from pymongo import MongoClient


class ImageRepository:
    def __init__(self, mongo_client: MongoClient):
        self.collection = mongo_client.get_database("microservice").get_collection(
            "image_uploads"
        )
        self.logger = logging.getLogger("image_service")

    def put_image(self, image: dict) -> ObjectId:
        result = self.collection.insert_one(image)
        return result.inserted_id

    def delete_image(self, uuid: UUID) -> bool:
        result = self.collection.delete_one({"uuid": str(uuid)})
        self.logger.info(f"Deleted image with uuid {uuid} from database")
        return result.deleted_count > 0

    def query_images(self, field_key: str, field_value: str) -> list:
        return list(self.collection.find({field_key: field_value}))

    def query_image(self, field_key: str, field_value: str) -> dict:
        return self.collection.find_one({field_key: field_value})
