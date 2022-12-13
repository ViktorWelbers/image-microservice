from collections import namedtuple
from unittest import TestCase
from unittest.mock import Mock, sentinel

from pymongo import MongoClient
from pymongo.collection import Collection

from app.repositories import ImageRepository


class TestImageRepository(TestCase):
    def setUp(self) -> None:
        self.mongo_client = Mock(MongoClient)
        self.repository = ImageRepository(mongo_client=self.mongo_client)
        self.collection = Mock(Collection)
        self.repository.collection = self.collection

    def test_put_image(self) -> None:
        database_result = namedtuple("obj", ["inserted_id"])(sentinel.id)

        self.collection.insert_one.return_value = database_result

        result = self.repository.put_image({sentinel.key: sentinel.value})

        self.collection.insert_one.assert_called_once_with(
            {sentinel.key: sentinel.value}
        )
        self.assertEqual(result, sentinel.id)

    def test_delete_image(self) -> None:
        database_result = namedtuple("obj", ["deleted_count"])(1)
        self.collection.delete_one.return_value = database_result

        result = self.repository.delete_image(sentinel.uuid)

        self.collection.delete_one.assert_called_once_with({"uuid": "sentinel.uuid"})
        self.assertEqual(result, 1)

    def test_query_images(self) -> None:
        database_result = [{"_id": sentinel.id, "uuid": sentinel.uuid}]
        self.collection.find.return_value = database_result

        result = self.repository.query_images(sentinel.key, sentinel.value)

        self.collection.find.assert_called_once_with({sentinel.key: sentinel.value})
        self.assertEqual(result, database_result)

    def test_query_image(self) -> None:
        database_result = {"_id": sentinel.id, "uuid": sentinel.uuid}
        self.collection.find_one.return_value = database_result

        result = self.repository.query_image(sentinel.key, sentinel.value)

        self.collection.find_one.assert_called_once_with({sentinel.key: sentinel.value})
        self.assertEqual(result, database_result)
