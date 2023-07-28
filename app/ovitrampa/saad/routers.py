from fastapi import APIRouter
from app.config import get_settings
from app.ovitrampa.models import Saads, SaadsOut

settings = get_settings()

router = APIRouter(
    prefix="/saads",
    tags=["saads"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[SaadsOut])
async def get_saads():
    return await SaadsOut.from_queryset(Saads.all())
