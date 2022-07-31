from unittest import TestCase
from unittest.mock import patch, mock_open, sentinel, ANY
from uuid import uuid4

from fastapi.testclient import TestClient
from requests import Response
from starlette.responses import JSONResponse

from app.main import app
from app.models import ImageDocument


class TestHandler(TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def _check_successful_response(self, response: Response,
                                   expected_response_json: dict | ImageDocument | list) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_json)

    @patch('app.api.ImageUploadUseCase.upload')
    def test_upload_image(self, mock_image_upload) -> None:
        with patch("builtins.open", mock_open()):
            expected = {'uuid': 'test_uuid'}
            mock_image_upload.return_value = expected

            response = self.client.post('api/images/upload/test_client_id',
                                        files={'file': ('filename', open(sentinel.path), 'image/jpeg')})

            mock_image_upload.assert_called_once_with(ANY, 'test_client_id')
            self._check_successful_response(response, expected)

    @patch('app.api.ImageDeleteUseCase.delete_image_uuid')
    def test_delete_image(self, mock_delete_image) -> None:
        uuid = uuid4()
        expected = {'Result': 'OK'}
        mock_delete_image.return_value = expected

        response = self.client.post(f'api/images/delete/?uuid={uuid}')

        mock_delete_image.assert_called_once_with(uuid)
        self._check_successful_response(response, expected)

    @patch('app.api.ImageRetrievalUseCase.get_images_for_client_id')
    def test_get_images_for_client_id(self, mock_get_images) -> None:
        expected = [ImageDocument(
            uuid='test_uuid',
            file_name='test_file_name',
            file_path='test_file_path',
            content_type='test_content_type',
            client_id='test_client_id'
        )]
        mock_get_images.return_value = expected

        response = self.client.get('api/images/get_images/?client_id=test_client_id')

        mock_get_images.assert_called_once_with('test_client_id')
        self._check_successful_response(response, expected)

    @patch('app.api.ImageRetrievalUseCase.get_image_for_uuid')
    def test_get_image_for_uuid(self, mock_get_image) -> None:
        uuid = uuid4()
        expected = ImageDocument(
            uuid='test_uuid',
            file_name='test_file_name',
            file_path='test_file_path',
            content_type='test_content_type',
            client_id='test_client_id'
        )
        mock_get_image.return_value = expected

        response = self.client.get(f'api/images/get_image/?uuid={uuid}')

        mock_get_image.assert_called_once_with(uuid)
        self._check_successful_response(response, expected)

    @patch('app.api.serve_file')
    def test_download_image_uuid(self, handle_image) -> None:
        with patch('app.api.ImageRetrievalUseCase.get_image_for_uuid') as mock_download_image:
            uuid = uuid4()
            mock_download_image.return_value = sentinel.download_image
            handle_image.return_value = JSONResponse({'Result': 'IMAGE'})

            response = self.client.get(f'api/images/download/{uuid}')

            mock_download_image.assert_called_once_with(uuid)
            handle_image.assert_called_once_with(sentinel.download_image)
            self.assertEqual(response.json(), {'Result': 'IMAGE'})
