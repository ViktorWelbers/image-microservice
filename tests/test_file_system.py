from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, sentinel
from uuid import uuid4

from app.configuration import get_settings
from app.entities import FileManagement


class TestFileSystem(TestCase):
    def test_get_root(self) -> None:
        self.assertEqual(FileManagement._get_root(), Path(__file__).parent.parent)

    @patch("app.entities.FileManagement._get_root")
    def test_get_file_directory_when_directory_exists(self, mock_get_root) -> None:
        mock_get_root.return_value = "/tmp"
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            with patch.object(Path, "mkdir") as mock_mkdir:
                result = FileManagement._get_file_directory()

                self.assertEqual(result, Path("/tmp", get_settings().upload_folder))
                mock_exists.assert_called_once()
                mock_mkdir.assert_not_called()
                mock_get_root.assert_called_once()

    @patch("app.entities.FileManagement._get_root")
    def test_get_file_directory_when_directory_does_not_exist(
        self, mock_get_root
    ) -> None:
        mock_get_root.return_value = "/tmp"
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            with patch.object(Path, "mkdir") as mock_mkdir:
                result = FileManagement._get_file_directory()

                self.assertEqual(result, Path("/tmp", get_settings().upload_folder))
                mock_exists.assert_called_once()
                mock_mkdir.assert_called_once()
                mock_get_root.assert_called_once()

    @patch("app.entities.FileManagement._get_file_directory")
    def test_get_file(self, mock_get_file_directory) -> None:
        with patch.object(Path, "iterdir") as mock_iterdir:
            mock_iterdir.return_value = [sentinel.file, sentinel.second_file]

            result = FileManagement.get_file(sentinel.uuid)

            self.assertEqual(result, sentinel.file)

    @patch("app.entities.FileManagement._get_file_directory", return_value=Path("/tmp"))
    def test_generate_filepath(self, mock_file_directory) -> None:
        with patch.object(Path, "mkdir") as mock_mkdir:
            uuid = uuid4()

            result = FileManagement.generate_filepath(uuid, "filename")

            mock_mkdir.assert_called_once()
            mock_file_directory.assert_called_once()
            self.assertEqual(result, Path("/tmp", str(uuid), "filename"))

    @patch("app.entities.FileManagement._get_root", return_value=Path("/tmp"))
    def test_remove_file(self, mock_get_root) -> None:
        with patch("shutil.rmtree") as mock_rmtree:
            FileManagement.remove_file("uuid")

            mock_rmtree.assert_called_once_with(
                Path("/tmp", get_settings().upload_folder, "uuid")
            )
            mock_get_root.assert_called_once()

    @patch("app.entities.FileManagement._get_file_directory")
    @patch("app.entities.FileManagement._get_root", return_value=Path("/tmp"))
    def test_list_all_files(self, mock_get_root, mock_get_file_directory) -> None:
        with patch.object(Path, "iterdir") as mock_iterdir:
            with self.assertLogs(FileManagement.logger, level="INFO") as logs:
                mock_iterdir.return_value = [sentinel.file, sentinel.second_file]

                FileManagement.list_all_files()

                self.assertEqual(
                    logs.output[0],
                    "INFO:image_service:file with path: sentinel.file found",
                )
                self.assertEqual(
                    logs.output[1],
                    "INFO:image_service:file with path: sentinel.second_file found",
                )
                self.assertEqual(
                    logs.output[2], "INFO:image_service:Found a total of 2 files"
                )
                mock_get_root.assert_called_once()
                mock_get_file_directory.assert_called_once()
