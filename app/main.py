import logging
from logging.config import dictConfig
from typing import Callable
from urllib.request import Request

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from app.routes import router as api_router
from app.settings import LogConfig
from app.settings import get_settings


def use_route_names_as_operation_ids(fast_app: FastAPI) -> None:
    for route in fast_app.routes:
        if isinstance(route, APIRoute):
            route.path = route.path.replace(get_settings().base_url, "")
            route.path_format = route.path.replace(get_settings().base_url, "")
            route.operation_id = route.name


dictConfig(LogConfig().dict())
logger = logging.getLogger(get_settings().logger_name)

app = FastAPI(
    title="Microservice for Uploading Images to MongoDB and FileSystem",
    description="This is a microservice which is handling images",
    version="1.0",
    servers=[{"url": get_settings().base_url, "description": "Base Url"}],
)


@app.middleware("http")
async def check_api_key(request: Request, call_next: Callable) -> Response:
    if (
        request.headers.get("Authorization") != get_settings().api_key
        and request.method != "OPTIONS"
        and request.method != "POST"
    ):
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=get_settings().base_url)
use_route_names_as_operation_ids(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=5000)
