from typing import Protocol, Any

import requests
from requests import Response


class HttpClient(Protocol):
    def get(self, params: Any) -> Response:
        ...


class AuthenticationHttpClient(HttpClient):
    def __init__(self, url):
        self.url = url

    def get(self, auth_token: str) -> Response:
        return requests.get(self.url, headers={"Authorization": auth_token})
