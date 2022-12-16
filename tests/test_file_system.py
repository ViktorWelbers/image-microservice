from unittest import TestCase
from unittest.mock import sentinel

from app.file_system import AzureFileSystem


class TestFileSystem(TestCase):
    def setUp(self) -> None:
        self.file_system = AzureFileSystem(
            sentinel.account_name, sentinel.account_key, sentinel.share_name
        )
