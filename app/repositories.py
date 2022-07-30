from uuid import UUID

from bson import ObjectId
from pymongo import MongoClient


class ImageRepository:
    def __init__(self, mongo_client: MongoClient):
        self.collection = mongo_client.get_database('images').get_collection('uploads')

    def store_image(self, image: dict) -> ObjectId:
        result = self.collection.insert_one(image)
        return result.inserted_id

    def delete_image(self, uuid: UUID) -> int:
        result = self.collection.delete_one({'uuid': str(uuid)})
        return result.deleted_count

    def query_images(self, field_value: UUID | str, field_key: str) -> list:
        return list(self.collection.find({field_key: field_value}))
