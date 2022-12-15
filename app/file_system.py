from uuid import UUID

from azure.storage.file import ContentSettings
from azure.storage.file import FileService
from starlette.responses import FileResponse

from app.models import ImageDocument


class AzureFileSystem:
    def __init__(self, account_name: str, account_key: str, share_name: str):
        self.share_name = share_name
        self.file_service = FileService(
            account_name=account_name, account_key=account_key
        )

    def create_directories(self, client_id: str, uuid: str) -> None:
        generator = self.file_service.list_directories_and_files(self.share_name)
        if client_id not in [x.name for x in generator]:
            self.file_service.create_directory(self.share_name, client_id)
        self.file_service.create_directory(self.share_name, client_id + "/" + uuid)

    def upload_file(
        self,
        file_name: str,
        file_content: bytes,
        uuid: UUID,
        client_id: str,
    ) -> None:
        self.create_directories(client_id, str(uuid))
        remote_directory = client_id + "/" + str(uuid)
        self.file_service.create_file_from_bytes(
            share_name=self.share_name,
            directory_name=remote_directory,
            file_name=file_name,
            file=file_content,
            content_settings=ContentSettings(
                content_type=f"image/{file_name.split('.')[-1]}"
            ),
        )

    def download_file(
        self, file_name: str, remote_directory: str | None = None
    ) -> bytes:
        return self.file_service.get_file_to_bytes(
            self.share_name, remote_directory, file_name
        ).content

    def delete_file(self, file_name: str, remote_directory: str | None = None) -> None:
        self.file_service.delete_file(self.share_name, remote_directory, file_name)


def serve_file(image_document: ImageDocument) -> FileResponse:
    return FileResponse(
        path=image_document.file_path,
        filename=image_document.file_name,
        media_type=image_document.content_type,
    )
