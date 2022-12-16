from unittest import TestCase

from app.schemas import ImageDocument


class TestModels(TestCase):
    def setUp(self) -> None:
        self.image_document = ImageDocument(
            file_path="test_file_path",
            uuid="test_uuid",
            client_id="test_client_id",
            file_name="test_file_name",
            content_type="test_content_type",
            tags={"test_tag": "test_value"},
        )

    def test_fields_image_document(self) -> None:
        self.assertEqual(self.image_document.file_path, "test_file_path")
        self.assertEqual(self.image_document.uuid, "test_uuid")
        self.assertEqual(self.image_document.client_id, "test_client_id")
        self.assertEqual(self.image_document.file_name, "test_file_name")
        self.assertEqual(self.image_document.content_type, "test_content_type")
        self.assertEqual(self.image_document.tags, {"test_tag": "test_value"})

    def test_fields_image_document_tags_not_mandatory(self) -> None:
        image = ImageDocument(
            file_path="test_file_path",
            uuid="test_uuid",
            client_id="test_client_id",
            file_name="test_file_name",
            content_type="test_content_type",
        )

        self.assertEqual(image.dict()["tags"], None)
