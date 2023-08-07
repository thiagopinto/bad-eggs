from fastapi import APIRouter, HTTPException, status, Form, UploadFile
from app.models import Status
from app.config import get_settings
from datetime import datetime
from typing import Annotated
from app.yolo.services import storage, delete
from app.ovitrampa.models import Images, ImagesOut, Segments
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from tortoise.functions import Sum


settings = get_settings()

router = APIRouter(
    prefix="/images",
    tags=["images"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[ImagesOut])
async def get_cycle_images(cycle_id: int = 0):

    return await paginate(
        query=Images.filter(cycle_id=cycle_id)
        .prefetch_related("cycle", "segments")
        .order_by("-updated_at")
        .all().annotate(
            eggs=Sum("segments__eggs"),
            bad_eggs=Sum("segments__bad_eggs")
        )
        # prefetch_related=["saad"]
    )


@router.get("/{cycle_image_id}", response_model=ImagesOut)
async def get_cycle(cycle_image_id: int):
    try:
        return await Images.get(id=cycle_image_id).prefetch_related("cycle", "segments").annotate(
            eggs=Sum("segments__eggs"),
            bad_eggs=Sum("segments__bad_eggs")
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.post("/", response_model=list[ImagesOut])
async def create_cycle(
    cycle_id: Annotated[int, Form()],
    files: list[UploadFile],
):
    cycle_images = await storage(date=datetime.today().strftime(
        "%Y-%m-%d"), files=files, cycle_id=cycle_id)
    images = []

    for cycle_image in cycle_images:
        images.append(await Images.get(id=cycle_image.id).prefetch_related("cycle", "segments").annotate(
            eggs=Sum("segments__eggs"),
            bad_eggs=Sum("segments__bad_eggs")
        )
        )

    return images


@router.delete("/{cycle_image_id}", response_model=Status)
async def delete_cycle(cycle_image_id: int):
    try:
        cycle_image = await Images.get(id=cycle_image_id).prefetch_related("segments")

        is_delete = delete(cycle_image)
        if is_delete:
            for segment in cycle_image.segments:
                deleted_count = await Segments.filter(id=segment.id).delete()
            deleted_count = await Images.filter(id=cycle_image_id).delete()
            if not deleted_count:
                raise HTTPException(
                    status_code=404, detail=f"Cycle {cycle_image_id} not found"
                )
        else:
            raise HTTPException(
                status_code=404, detail=f"Cycle {cycle_image_id} not found"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cycle {cycle_image_id} not found",
        )
    return Status(message=f"Deleted cycle {cycle_image_id}")
