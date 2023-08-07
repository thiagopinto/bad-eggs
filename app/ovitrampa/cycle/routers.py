from fastapi import APIRouter, HTTPException, status
from app.models import Status
from app.config import get_settings
from datetime import datetime
from app.ovitrampa.models import Cycles, CyclesIn, CyclesOut, Ovitrampas, Segments, Images
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from tortoise.functions import Sum
from app.yolo.services import delete


settings = get_settings()

router = APIRouter(
    prefix="/cycles",
    tags=["cycles"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[CyclesOut])
async def get_cycles(ovitrampa_id: int = 0):

    return await paginate(
        query=Cycles.filter(ovitrampa_id=ovitrampa_id)
        .prefetch_related("ovitrampa")
        .order_by("-start")
        .all()
        # .annotate(
        #    eggs=Sum("images__segments__eggs"),
        #    bad_eggs=Sum("images__segments__bad_eggs")
        # )
        # prefetch_related=["saad"]
    )


@router.get("/{cycle_id}", response_model=CyclesOut)
async def get_cycle(cycle_id: int):
    try:
        return await Cycles.get(id=cycle_id).prefetch_related("ovitrampa").annotate(
            eggs=Sum("images__segments__eggs"),
            bad_eggs=Sum("images__segments__bad_eggs")
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.post("/", response_model=CyclesOut)
async def create_cycle(cycleIn: CyclesIn):
    cycle = await Cycles(**cycleIn.dict())
    await cycle.save()
    return cycle


@router.put("/{cycle_id}", response_model=CyclesOut)
async def update_cycle(cycle_id: int, cycleIn: CyclesIn):
    try:
        cycle = await Cycles.get(id=cycle_id)
        cycle.start = cycleIn.start
        cycle.end = cycleIn.end
        cycle.updated_at = datetime.now()
        await cycle.save()

        return cycle
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.delete("/{cycle_id}", response_model=Status)
async def delete_cycle(cycle_id: int):
    try:
        cycle = await Cycles.get(id=cycle_id)

        for image in await cycle.images:
            is_delete = delete(image)
            if is_delete:          
                for segment in await image.segments:
                    deleted_count = await Segments.filter(id=segment.id).delete()
                deleted_count = await Images.filter(id=image.id).delete()

        deleted_count = await Cycles.filter(id=cycle_id).delete()
        if not deleted_count:
            raise HTTPException(
                status_code=404, detail=f"Cycle {cycle_id} not found"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cycle {cycle_id} not found",
        )
    return Status(message=f"Deleted cycle {cycle_id}")
