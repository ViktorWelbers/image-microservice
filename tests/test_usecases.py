from io import BytesIO
from unittest import TestCase
from unittest.mock import Mock, patch, sentinel, ANY

from PIL import Image

from app.file_system import AzureFileSystem
from app.repositories import ImageRepository
from app.usecases import (
    ImageUploadUseCase,
    ImageDeleteUseCase,
    ImageDownloadUseCase,
    ImageMetadataUseCase,
)


class TestImageUploadUseCase(TestCase):
    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_system = Mock(AzureFileSystem)
        self.use_case = ImageUploadUseCase(self.repository, self.file_system)

    @patch("app.usecases.uuid4")
    def test_upload(self, mock_uuid4) -> None:
        # when
        bytes_io = BytesIO()
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(bytes_io, "PNG")
        bytes_io.seek(0)
        mock_uuid4.return_value = sentinel.uuid
        file = Mock()
        file_content = bytes_io.read()
        file.file.read.return_value = file_content
        file.filename = "test.png"
        file.content_type = "image/png"

        # when
        self.use_case.execute(
            file, "test_client_id", sentinel.processed, sentinel.origin_uuid
        )

        # then
        self.repository.put_image.assert_called_with(
            {
                "file_path": "test_client_id/sentinel.uuid",
                "uuid": "sentinel.uuid",
                "client_id": "test_client_id",
                "file_name": "test.png",
                "content_type": "image/png",
                "tags": ANY
            }
        )

        self.file_system.upload_file.assert_called_with(
            file_name="test.png",
            file_content=file_content,
            client_id="test_client_id",
            uuid=sentinel.uuid,
        )


class TestImageDeleteUseCase(TestCase):
    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_system = Mock(AzureFileSystem)
        self.use_case = ImageDeleteUseCase(self.repository, self.file_system)

    def test_delete_image_uuid_success(self) -> None:
        self.repository.query_image.return_value = {
            "file_path": "test_client_id/sentinel.uuid",
            "file_name": "test.png",
        }

        result = self.use_case.execute(sentinel.uuid)

        self.repository.query_image.assert_called_with(
            field_key="uuid", field_value="sentinel.uuid"
        )
        self.file_system.delete_file.assert_called_with(
            file_name="test.png", file_path="test_client_id/sentinel.uuid"
        )
        self.repository.delete_image.assert_called_with(sentinel.uuid)
        self.assertEqual(True, result)

    def test_delete_image_uuid_no_success(self) -> None:
        self.repository.query_image.return_value = False

        result = self.use_case.execute(sentinel.uuid)

        self.repository.query_image.assert_called_with(
            field_key="uuid", field_value="sentinel.uuid"
        )
        self.file_system.delete_file.assert_not_called()
        self.repository.delete_image.assert_not_called()
        self.assertEqual(False, result)


class ImageMetaDataUseCase(TestCase):
    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_system = Mock(AzureFileSystem)
        self.use_case = ImageMetadataUseCase(self.repository, self.file_system)

    def test_get_images_for_client_id(self) -> None:
        self.repository.query_images.return_value = sentinel.result

        result = self.use_case.execute(sentinel.client_id)

        self.repository.query_images.assert_called_with("client_id", sentinel.client_id)
        self.assertEqual(sentinel.result, result)


class TestImageDownloadUseCase(TestCase):
    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_system = Mock(AzureFileSystem)
        self.use_case = ImageDownloadUseCase(self.repository, self.file_system)

    def test_download_image(self) -> None:
        self.repository.query_image.return_value = {
            "file_path": "test_client_id/sentinel.uuid",
            "file_name": "test.png",
        }
        self.file_system.download_file.return_value = sentinel.file_content

        result = self.use_case.execute(sentinel.uuid)

        self.repository.query_image.assert_called_with(
            field_key="uuid", field_value="sentinel.uuid"
        )
        self.file_system.download_file.assert_called_with(
            file_name="test.png", file_path="test_client_id/sentinel.uuid"
        )
        self.assertEqual(sentinel.file_content, result)

    def test_download_image_with_invalid_uuid(self) -> None:
        self.repository.query_image.return_value = {}

        result = self.use_case.execute(sentinel.uuid)

        self.repository.query_image.assert_called_with(
            field_key="uuid", field_value="sentinel.uuid"
        )
        self.file_system.download_file.assert_not_called()
        self.assertEqual((None, None), result)
