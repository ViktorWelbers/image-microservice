import logging
import shutil
from pathlib import Path
from uuid import UUID

from starlette.responses import FileResponse

from app.configuration import get_settings
from app.models import ImageDocument


class FileManagement:
    logger = logging.getLogger(get_settings().logger_name)

    @staticmethod
    def _get_root() -> Path:
        return Path(__file__).parent.parent

    @classmethod
    def _get_file_directory(cls):
        directory = Path(cls._get_root(), get_settings().upload_folder)
        if not directory.exists():
            directory.mkdir()
        return directory

    @classmethod
    def get_file(cls, uuid: UUID) -> Path:
        folder = Path(cls._get_file_directory(), str(uuid))
        for child in folder.iterdir():
            return child

    @classmethod
    def generate_filepath(cls, uuid: UUID, filename: str) -> Path:
        folder = Path(cls._get_file_directory(), str(uuid))
        folder.mkdir()
        return Path(folder, filename)

    @classmethod
    def remove_file(cls, uuid: str):
        temp = Path(cls._get_root(), get_settings().upload_folder, uuid)
        try:
            shutil.rmtree(temp)
            cls.logger.info(f"Removed file {temp} from filesystem")
        except Exception as e:
            cls.logger.error(f"Error removing file {temp} from filesystem: {e}")

    @classmethod
    def list_all_files(cls):
        cls._get_file_directory()
        folder = Path(cls._get_root(), get_settings().upload_folder)
        for child in folder.iterdir():
            cls.logger.info(f"file with path: {child} found")
        cls.logger.info(f"Found a total of {len(list(folder.iterdir()))} files")


def serve_file(image_document: ImageDocument) -> FileResponse:
    return FileResponse(
        path=image_document.file_path,
        filename=image_document.file_name,
        media_type=image_document.content_type,
    )
