from unittest import result
from fastapi import APIRouter, HTTPException, status
from sympy import true
from app.models import Status
from app.config import get_settings
from datetime import datetime
from app.ovitrampa import saad
from app.ovitrampa.cycle.routers import router as cycle_router
from app.ovitrampa.cycle_image.routers import router as cycle_image_router
from app.ovitrampa.models import Ovitrampas, OvitrampasIn, OvitrampasOut, OvitrampasWithSaad
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

settings = get_settings()

router = APIRouter(
    prefix="/ovitrampas",
    tags=["ovitrampas"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[OvitrampasWithSaad])
async def get_ovitrampas():

    return await paginate(
        query=Ovitrampas.all().prefetch_related("saad").order_by("-updated_at"),
        # prefetch_related=["saad"]
    )


@router.get("/{ovitrampa_id}", response_model=OvitrampasWithSaad)
async def get_ovitrampa(ovitrampa_id: int):
    try:
        return await OvitrampasWithSaad.from_queryset_single(
            Ovitrampas.get(id=ovitrampa_id)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ovitrampa not found"
        )


@router.post("/", response_model=OvitrampasWithSaad)
async def create_ovitrampa(ovitrampasIn: OvitrampasIn):
    ovitrampa = await Ovitrampas(**ovitrampasIn.dict())
    await ovitrampa.save()

    return await OvitrampasWithSaad.from_tortoise_orm(ovitrampa)


@router.put("/{ovitrampa_id}", response_model=OvitrampasWithSaad)
async def update_ovitrampa(ovitrampa_id: int, ovitrampaIn: OvitrampasIn):
    try:
        ovitrampa = await Ovitrampas.get(id=ovitrampa_id)
        ovitrampa.description = ovitrampaIn.description
        ovitrampa.address = ovitrampaIn.address
        ovitrampa.neighborhood = ovitrampaIn.neighborhood
        ovitrampa.saad_id = ovitrampaIn.saad_id
        ovitrampa.disabled = ovitrampaIn.disabled
        ovitrampa.updated_at = datetime.now()
        await ovitrampa.save()

        return await OvitrampasWithSaad.from_tortoise_orm(ovitrampa)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ovitrampa not found"
        )


@router.delete("/{ovitrampa_id}", response_model=Status)
async def delete_ovitrampa(ovitrampa_id: int):
    try:
        deleted_count = await Ovitrampas.filter(id=ovitrampa_id).delete()
        if not deleted_count:
            raise HTTPException(
                status_code=404, detail=f"Ovitrampa {ovitrampa_id} not found"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ovitrampa {ovitrampa_id} not found",
        )
    return Status(message=f"Deleted ovitrampa {ovitrampa_id}")


router.include_router(cycle_router)
router.include_router(cycle_image_router)
