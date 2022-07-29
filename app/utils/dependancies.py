from app.usecases import ImageUseCase
from app.repositories import db


async def get_image_use_case():
    return ImageUseCase(db)
