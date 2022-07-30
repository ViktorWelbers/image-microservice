from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    upload_folder = "files"
    user_folder = "projects"
    base_url = "/api"
    log_level = "INFO"
    mongo_url = "mongodb://mongodb:27017/admin"
    mongo_password = "password"
    mongo_user = "admin"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


