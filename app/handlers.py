from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import UploadFile
from starlette.responses import Response, JSONResponse

from app.http_client import HttpClient
from app.schemas import ImageDocument
from app.usecases import (
    ImageUseCase,
)


class Handler(ABC):
    def __init__(self, use_case: ImageUseCase):
        self.use_case = use_case

    @abstractmethod
    def handle(self, *args, **kwargs) -> Response:
        ...


class UploadHandler(Handler):
    def __init__(self, use_case: ImageUseCase, http_client: HttpClient):
        super().__init__(use_case)
        self.http_client = http_client

    def handle(
        self,
        file: UploadFile,
        user_token: str,
        processed: bool,
        origin_uuid: str | UUID | None,
    ) -> JSONResponse:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            return JSONResponse(
                content={"error": "Only jpeg and png images are allowed"},
                status_code=400,
            )
        resp = self.http_client.get(user_token)
        if resp.status_code != 200:
            return JSONResponse(
                content={"error": "Invalid user token"}, status_code=400
            )
        content = self.use_case.execute(file, resp.json(), processed, origin_uuid)
        return JSONResponse(content=content, media_type="application/json")


class DeleteHandler(Handler):
    def handle(self, uuid: UUID) -> JSONResponse:
        content = self.use_case.execute(uuid)
        if content:
            return JSONResponse(
                content={"message": f"{uuid} was deleted"},
                media_type="application/json",
            )
        return JSONResponse(content={"error": "Image not found"}, status_code=404)


class MetadataHandler(Handler):
    def handle(self, client_id: str) -> list[ImageDocument]:
        content = self.use_case.execute(client_id)
        return [ImageDocument(**image) for image in content]


class DownloadHandler(Handler):
    def handle(self, uuid: UUID) -> Response:
        content, file_extension = self.use_case.execute(uuid)
        if content is None:
            return Response(content={"error": "Image not found"}, status_code=404)
        return Response(content=content, media_type=f"image/{file_extension}")
