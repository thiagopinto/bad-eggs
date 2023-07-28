from fastapi import APIRouter, Form, UploadFile
from app.config import get_settings
from typing import Annotated
from datetime import date
from app.yolo.services import storage

settings = get_settings()

router = APIRouter(
    prefix="/yolo",
    tags=["yolo"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def upload_image(
    date: Annotated[date, Form()],
    description: Annotated[str, Form()],
    files: list[UploadFile],
):
    counts = storage(date=date, files=files)

    return counts
