import json
from unittest import TestCase
from unittest.mock import patch, mock_open, sentinel, ANY, Mock
from uuid import uuid4

import fastapi.responses
from fastapi.testclient import TestClient
from requests import Response
from starlette.responses import JSONResponse

from app.dependencies import (
    get_upload_handler,
    get_delete_handler,
    get_metadata_handler,
    get_download_handler,
)
from app.main import app
from app.schemas import ImageDocument


class TestHandler(TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.handler = Mock()

    def _check_successful_response(
        self, response: Response, expected_response_json: dict | ImageDocument | list
    ) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_json)

    def test_upload_image(self) -> None:
        with patch("builtins.open", mock_open()):
            expected = {"uuid": "test_uuid"}
            self.handler.handle.return_value = expected
            app.dependency_overrides[get_upload_handler] = lambda: self.handler

            response = self.client.post(
                "api/images/upload/test_client_id",
                files={"file": ("filename", open(sentinel.path), "image/jpeg")},
            )

            self.handler.handle.assert_called_once_with(ANY, "test_client_id", False)
            self._check_successful_response(response, expected)

    def test_delete_image(self) -> None:
        uuid = uuid4()
        expected = {"Result": "OK"}
        self.handler.handle.return_value = expected
        app.dependency_overrides[get_delete_handler] = lambda: self.handler

        response = self.client.post(f"api/images/delete/{uuid}")

        self.handler.handle.assert_called_once_with(uuid)
        self._check_successful_response(response, expected)

    def test_get_images_for_client_id(self) -> None:
        expected = [
            ImageDocument(
                uuid="test_uuid",
                file_name="test_file_name",
                file_path="test_file_path",
                content_type="test_content_type",
                client_id="test_client_id",
            )
        ]
        self.handler.handle.return_value = expected
        app.dependency_overrides[get_metadata_handler] = lambda: self.handler

        response = self.client.get("api/images/images_metadata/test_client_id")

        self.handler.handle.assert_called_once_with("test_client_id")
        self._check_successful_response(response, expected)

    def test_download_image_uuid(self) -> None:
        uuid = uuid4()
        self.handler.handle.return_value = fastapi.responses.Response(
            content=json.dumps({"Result": "IMAGE"})
        )
        app.dependency_overrides[get_download_handler] = lambda: self.handler

        response = self.client.get(f"api/images/download/{uuid}")

        self.handler.handle.assert_called_once_with(uuid)
        self.assertEqual(response.json(), {"Result": "IMAGE"})
