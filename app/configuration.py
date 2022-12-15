import os
from functools import lru_cache
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    upload_folder = "files"
    base_url = "/api"
    log_level = "INFO"
    mongo_url = "mongodb://mongodb:27017/admin"
    mongo_password = "password"
    mongo_user = "admin"
    logger_name = "image_service"
    azure_account_name = os.getenv("AZURE_ACCOUNT_NAME")
    azure_account_key = os.getenv("AZURE_ACCOUNT_KEY")
    azure_share_name = os.getenv("AZURE_SHARE_NAME")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = get_settings().logger_name
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = get_settings().log_level

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }
