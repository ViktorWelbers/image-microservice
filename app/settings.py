import os
from functools import lru_cache
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    base_url = "/api"
    log_level = "INFO"
    logger_name = "image_service"
    api_key: str = os.getenv("API_KEY")
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME")
    mongo_collection: str = os.getenv("MONGO_COLLECTION")
    azure_account_name: str = os.getenv("AZURE_ACCOUNT_NAME")
    azure_account_key: str = os.getenv("AZURE_ACCOUNT_KEY")
    azure_share_name: str = os.getenv("AZURE_SHARE_NAME")


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
