import logging
import shutil
from pathlib import Path
from uuid import UUID

from app.utils.configuration import get_settings


class FileManagement:
    logger = logging.getLogger(get_settings().logger_name)

    @classmethod
    @staticmethod
    def _get_root():
        return Path(__file__).parent.parent.parent

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
            cls.logger.info(f'Removed file {temp} from filesystem')
        except Exception as e:
            cls.logger.error(f'Error removing file {temp} from filesystem: {e}')

    @classmethod
    def list_all_files(cls):
        cls._get_file_directory().iterdir()
        folder = Path(cls._get_root(), get_settings().upload_folder)
        for child in folder.iterdir():
            cls.logger.info(f'file with path: {child} found')
        cls.logger.info(f'Found a total of {len(list(folder.iterdir()))} files')
