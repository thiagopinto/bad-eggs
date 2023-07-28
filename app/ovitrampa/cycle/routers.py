from fastapi import APIRouter, HTTPException, status
from app.models import Status
from app.config import get_settings
from datetime import datetime
from app.ovitrampa.models import Cycles, CyclesIn, CyclesOut, CyclesWithOvitrampa, Ovitrampas
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate


settings = get_settings()

router = APIRouter(
    prefix="/cycles",
    tags=["cycles"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[CyclesWithOvitrampa])
async def get_cycles(ovitrampa_id: int = 0):
    
    return await paginate(
        query=Cycles.filter(ovitrampa_id=ovitrampa_id).prefetch_related("ovitrampa").order_by("-start").all(),
        # prefetch_related=["saad"]
    )


@router.get("/{cycle_id}", response_model=CyclesOut)
async def get_cycle(cycle_id: int):
    try:
        return await CyclesOut.from_queryset_single(Cycles.get(id=cycle_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.post("/", response_model=CyclesOut)
async def create_cycle(cycleIn: CyclesIn):
    cycle = await Cycles(**cycleIn.dict())
    await cycle.save()

    return await CyclesOut.from_tortoise_orm(cycle)


@router.put("/{cycle_id}", response_model=CyclesOut)
async def update_cycle(cycle_id: int, cycleIn: CyclesIn):
    try:
        cycle = await Cycles.get(id=cycle_id)
        cycle.start = cycleIn.start
        cycle.end = cycleIn.end
        cycle.number = cycleIn.number
        cycle.ovitrampa_id = cycleIn.ovitrampa_id
        cycle.updated_at = datetime.now()
        await cycle.save()

        return await CyclesOut.from_tortoise_orm(cycle)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )


@router.delete("/{cycle_id}", response_model=Status)
async def delete_cycle(cycle_id: int):
    try:
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
