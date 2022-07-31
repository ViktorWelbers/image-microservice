from collections import namedtuple
from unittest import TestCase
from unittest.mock import Mock, patch, sentinel

from app.entities import FileManagement
from app.models import ImageDocument
from app.repositories import ImageRepository
from app.usecases import ImageUploadUseCase, ImageDeleteUseCase, ImageRetrievalUseCase


class TestImageUploadUseCase(TestCase):

    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_management = Mock(FileManagement)
        self.use_case = ImageUploadUseCase(self.repository, self.file_management)

    @patch('app.usecases.uuid4')
    def test_upload(self, mock_uuid4) -> None:
        with patch('app.usecases.ImageUploadUseCase._store_image_in_filesystem') as mock_store_image_in_filesystem:
            with patch('app.usecases.ImageUploadUseCase._extract_meta_data_from_image') as mock_meta_data_from_image:
                file = namedtuple('filename', ['filename', 'content_type'])('test.jpg', 'image/jpeg')
                mock_uuid4.return_value = 'test_uuid'
                mock_store_image_in_filesystem.return_value = 'test_file_path'
                mock_meta_data_from_image.return_value = {'tags': 'meta_data'}

                self.use_case.upload(file, 'test_client_id')  # noqa: F
                self.repository.put_image.assert_called_with({
                    'file_path': 'test_file_path',
                    'uuid': 'test_uuid',
                    'client_id': 'test_client_id',
                    'file_name': 'test.jpg',
                    'content_type': 'image/jpeg',
                    'tags': {'tags': 'meta_data'}}
                )


class TestImageDeleteUseCase(TestCase):
    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_management = Mock(FileManagement)
        self.use_case = ImageDeleteUseCase(self.repository, self.file_management)

    def test_delete_image_uuid_success(self) -> None:
        self.repository.delete_image.return_value = True

        result = self.use_case.delete_image_uuid(sentinel.uuid)

        self.file_management.remove_file.assert_called_with(str(sentinel.uuid))
        self.repository.delete_image.assert_called_with(sentinel.uuid)
        self.assertEqual({'Result': 'OK'}, result)

    def test_delete_image_uuid_no_success(self) -> None:
        self.repository.delete_image.return_value = False

        result = self.use_case.delete_image_uuid(sentinel.uuid)

        self.file_management.remove_file.assert_not_called()
        self.repository.delete_image.assert_called_with(sentinel.uuid)
        self.assertEqual({'Result': 'NOT_FOUND'}, result)


class TestImageRetrievalUseCase(TestCase):
    def setUp(self) -> None:
        self.repository = Mock(ImageRepository)
        self.file_management = Mock(FileManagement)
        self.use_case = ImageRetrievalUseCase(self.repository, self.file_management)

    def test_get_images_for_client_id_returns_empty_list(self) -> None:
        self.repository.query_images.return_value = []

        result = self.use_case.get_images_for_client_id(sentinel.client_id)

        self.repository.query_images.assert_called_with('client_id', sentinel.client_id)
        self.assertEqual([], result)

    def test_get_images_for_client_id_returns_list_of_images(self) -> None:
        expected = {
            'uuid': 'test_uuid',
            'client_id': 'test_client_id',
            'file_name': 'test_file_name',
            'file_path': 'test_file_path',
            'content_type': 'test_content_type',
            'tags': {'tags': 'test_tags'}
        }
        self.repository.query_images.return_value = [expected]

        result = self.use_case.get_images_for_client_id(sentinel.client_id)

        self.repository.query_images.assert_called_with('client_id', sentinel.client_id)
        self.assertEqual([ImageDocument(**expected)], result)

    def test_get_image_for_uuid_returns_image(self) -> None:
        self.repository.query_image.return_value = None

        result = self.use_case.get_image_for_uuid(sentinel.uuid)

        self.repository.query_image.assert_called_with('uuid', 'sentinel.uuid')
        self.assertEqual(None, result)

    def test_get_image_for_uuid_returns_none(self) -> None:
        expected = {
            'uuid': 'test_uuid',
            'client_id': 'test_client_id',
            'file_name': 'test_file_name',
            'file_path': 'test_file_path',
            'content_type': 'test_content_type',
            'tags': {'tags': 'test_tags'}
        }
        self.repository.query_image.return_value = expected

        result = self.use_case.get_image_for_uuid(sentinel.uuid)

        self.repository.query_image.assert_called_with('uuid', 'sentinel.uuid')
        self.assertEqual(expected, result)
