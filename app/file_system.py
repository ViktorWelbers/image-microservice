from uuid import UUID

from azure.storage.file import ContentSettings
from azure.storage.file import FileService


class AzureFileSystem:
    def __init__(self, account_name: str, account_key: str, share_name: str):
        self.share_name = share_name
        self.file_service = FileService(
            account_name=account_name, account_key=account_key
        )

    def _create_directories(self, client_id: str, uuid: str) -> None:
        directories = self.file_service.list_directories_and_files(self.share_name)
        if client_id not in [path.name for path in directories]:
            self.file_service.create_directory(self.share_name, client_id)
        self.file_service.create_directory(self.share_name, client_id + "/" + uuid)

    def upload_file(
        self,
        file_name: str,
        file_content: bytes,
        uuid: UUID,
        client_id: str,
    ) -> None:
        self._create_directories(client_id, str(uuid))
        file_path = client_id + "/" + str(uuid)
        self.file_service.create_file_from_bytes(
            share_name=self.share_name,
            directory_name=file_path,
            file_name=file_name,
            file=file_content,  # type: ignore
            content_settings=ContentSettings(
                content_type=f"image/{file_name.split('.')[-1]}"
            ),
        )

    def download_file(self, file_name: str, file_path: str) -> tuple[bytes, str]:
        return (
            self.file_service.get_file_to_bytes(
                self.share_name, file_path, file_name
            ).content,
            file_name.split(".")[-1],
        )

    def delete_file(self, file_name: str, file_path: str) -> None:
        self.file_service.delete_file(self.share_name, file_path, file_name)
        self.file_service.delete_directory(self.share_name, file_path)
