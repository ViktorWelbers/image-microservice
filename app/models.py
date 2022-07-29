from pydantic import BaseModel


class Image(BaseModel):
    file_path: str
    uuid: str
    client_id: str
