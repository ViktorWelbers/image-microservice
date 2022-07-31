import logging
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.handler import router as api_router
from app.utils.configuration import LogConfig
from app.utils.configuration import get_settings
from app.utils.file_system_utils import FileManagement


def use_route_names_as_operation_ids(fast_app: FastAPI) -> None:
    for route in fast_app.routes:
        if isinstance(route, APIRoute):
            route.path = route.path.replace(get_settings().base_url, '')
            route.path_format = route.path.replace(get_settings().base_url, '')
            route.operation_id = route.name


dictConfig(LogConfig().dict())
logger = logging.getLogger(get_settings().logger_name)

app = FastAPI(
    title='Microservice for Uploading Images to MongoDB and FileSystem',
    description='This is a microservice which is handling images',
    version="1.0",
    servers=[
        {'url': get_settings().base_url, 'description': 'Base Url'}
    ])
app.include_router(api_router, prefix=get_settings().base_url)
use_route_names_as_operation_ids(app)


@app.on_event("startup")
async def startup_event():
    FileManagement.list_all_files()


if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
