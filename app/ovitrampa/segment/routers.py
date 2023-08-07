from fastapi import APIRouter, HTTPException, status, Form, UploadFile
from app.models import Status
from app.config import get_settings
from datetime import datetime
from typing import Annotated
from app.yolo.services import storage, delete
from app.ovitrampa.models import Segments, SegmentsIn, SegmentsOut
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate
from tortoise.functions import Sum


settings = get_settings()

router = APIRouter(
    prefix="/segments",
    tags=["segments"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.put("/{segment_id}", response_model=SegmentsOut)
async def update_cycle(segment_id: int, segmentIn: SegmentsIn):
    try:
        segment = await Segments.get(id=segment_id)
        if segmentIn.eggs is not None:
            segment.eggs = segmentIn.eggs

        if segmentIn.bad_eggs is not None:
            segment.bad_eggs = segmentIn.bad_eggs

        if segmentIn.false_positive is not None:
            segment.false_positive = segmentIn.false_positive

        if segmentIn.false_negative is not None:
            segment.false_negative = segmentIn.false_negative

        segment.updated_at = datetime.now()
        await segment.save()

        return await segment
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found"
        )
