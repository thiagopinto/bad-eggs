from itertools import cycle
from fastapi import APIRouter, HTTPException, status, Form, UploadFile
from app.models import Status
from app.config import get_settings
from datetime import datetime
from typing import Annotated
from app.ovitrampa import cycle_image
from app.yolo.services import storage, delete
from app.ovitrampa.models import CycleImages, CycleImagesOut
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

settings = get_settings()

router = APIRouter(
    prefix="/cycle_images",
    tags=["cycle_images"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[CycleImagesOut])
async def get_cycle_images(cycle_id: int = 0):
    return await paginate(
        query=CycleImages.filter(cycle_id=cycle_id).prefetch_related(
            "cycle").order_by("-updated_at").all(),
        # prefetch_related=["saad"]
    )


@router.get("/{cycle_image_id}", response_model=CycleImagesOut)
async def get_cycle(cycle_image_id: int):
    try:
        return await CycleImagesOut.from_queryset_single(
            CycleImages.get(id=cycle_image_id)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.post("/", response_model=list[CycleImagesOut])
async def create_cycle(
    cycle_id: Annotated[int, Form()],
    files: list[UploadFile],
):
    results = storage(date=datetime.today().strftime("%Y-%m-%d"), files=files)
    cycle_images = []
    for result in results:
        cycle_image = await CycleImages(
            eggs=result["counts"]["egg"],
            bad_eggs=result["counts"]["bad_egg"],
            file_name=result["file_name"],
            file_extension=result["file_extension"],
            cycle_id=cycle_id,
        )
        cycle = await cycle_image.cycle
        cycle.number = cycle.number + cycle_image.eggs
        await cycle.save()
        await cycle_image.save()
        cycle_images.append(cycle_image)

    return cycle_images


@router.put("/{cycle_image_id}", response_model=CycleImagesOut)
async def update_cycle(
    cycle_image_id, eggs: Annotated[int, Form()], bad_eggs: Annotated[int, Form()]
):
    try:
        cycle_image = await CycleImages.get(id=cycle_image_id)

        if eggs is not None:
            cycle_image.eggs = eggs

        if bad_eggs is not None:
            cycle_image.bad_eggs = bad_eggs

        cycle_image.updated_at = datetime.now()
        await cycle_image.save()

        return await CycleImagesOut.from_tortoise_orm(cycle_image)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.delete("/{cycle_image_id}", response_model=Status)
async def delete_cycle(cycle_image_id: int):
    try:
        cycle_image = await CycleImages.get(id=cycle_image_id)

        is_delete = delete(cycle_image)
        if is_delete:
            cycle = await cycle_image.cycle
            cycle.number = cycle.number - cycle_image.eggs
            await cycle.save()
            deleted_count = await CycleImages.filter(id=cycle_image_id).delete()
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
