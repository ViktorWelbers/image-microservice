from unittest import TestCase
from unittest.mock import patch

from app.http_client import AuthenticationHttpClient


class TestHttpClient(TestCase):
    def setUp(self) -> None:
        self.http_client = AuthenticationHttpClient("https://example.com")

    @patch("app.http_client.requests.get")
    def test_get(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "token"
        response = self.http_client.get("token")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "token")
        mock_get.assert_called_once_with(
            "https://example.com", headers={"Authorization": "token"}
        )
