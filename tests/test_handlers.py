from unittest import TestCase
from unittest.mock import Mock

from starlette.responses import JSONResponse

from app.handlers import UploadHandler, DeleteHandler, MetadataHandler, DownloadHandler
from app.http_client import HttpClient
from app.usecases import ImageUseCase


class TestUploadHandler(TestCase):
    def setUp(self) -> None:
        self.use_case = Mock(ImageUseCase)
        self.http_client = Mock(HttpClient)
        self.handler = UploadHandler(self.use_case, self.http_client)

    def test_handle_image_with_correct_file_type(self) -> None:
        # given
        file = Mock()
        file.content_type = "image/jpeg"
        self.http_client.get.return_value.status_code = 200
        self.http_client.get.return_value.json.return_value = {"client_id": "client_id"}
        user_token = "user_token"
        processed = True
        origin_uuid = "origin_uuid"
        self.use_case.execute.return_value = {"message": "success"}

        # when
        result = self.handler.handle(file, user_token, processed, origin_uuid)

        # then
        self.use_case.execute.assert_called_with(
            file, self.http_client.get(user_token).json(), processed, origin_uuid
        )
        self.http_client.get.assert_called_with(user_token)
        self.assertEqual(result.body, b'{"message":"success"}')

    def test_handle_image_with_incorrect_file_type(self) -> None:
        # given
        file = Mock()
        file.content_type = "text/plain"
        user_token = "user_token"
        processed = True
        origin_uuid = "origin_uuid"

        # when
        result = self.handler.handle(file, user_token, processed, origin_uuid)

        # then
        self.use_case.execute.assert_not_called()
        self.http_client.get.assert_not_called()
        self.assertEqual(
            result.body, b'{"error":"Only jpeg and png images are allowed"}'
        )


class TestDeleteHandler(TestCase):
    def setUp(self) -> None:
        self.use_case = Mock(ImageUseCase)
        self.handler = DeleteHandler(self.use_case)

    def test_handle_image_with_correct_uuid(self) -> None:
        # given
        uuid = "uuid"
        self.use_case.execute.return_value = True

        # when
        result = self.handler.handle(uuid)

        # then
        self.use_case.execute.assert_called_with(uuid)
        self.assertEqual(result.body, b'{"message":"uuid was deleted"}')

    def test_handle_image_with_incorrect_uuid(self) -> None:
        # given
        uuid = "uuid"
        self.use_case.execute.return_value = False

        # when
        result = self.handler.handle(uuid)

        # then
        self.use_case.execute.assert_called_with(uuid)
        self.assertEqual(result.body, b'{"error":"Image not found"}')


class TestDownloadHandler(TestCase):

    def setUp(self) -> None:
        self.use_case = Mock(ImageUseCase)
        self.handler = DownloadHandler(self.use_case)

    def test_handle_image_with_correct_uuid(self) -> None:
        # given
        uuid = "uuid"
        self.use_case.execute.return_value = "image", "image/jpeg"

        # when
        result = self.handler.handle(uuid)

        # then
        self.use_case.execute.assert_called_with(uuid)
        self.assertEqual(result.body, b'image')
