from pydantic import BaseModel
from pydantic.typing import Optional


class ImageDocument(BaseModel):
    file_path: str
    uuid: str
    client_id: str
    file_name: str
    content_type: str
    tags: Optional[dict] = None


class Payload(BaseModel):
    data: dict
