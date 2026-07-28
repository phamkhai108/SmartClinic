from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from smartclinic.api.deps_auth import CurrentUser, require_roles
from smartclinic.core.brain.brain_dto import PredictBrainResponse
from smartclinic.core.brain.brain_service import predict_image_class

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Brain"], prefix="/brain")


@router.post("/predict_tumor", response_model=PredictBrainResponse)
async def predict(
    _user: Annotated[CurrentUser, Depends(require_roles("doctor", "admin"))],
    file: Annotated[UploadFile, File()],
):
    if not file.filename or not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(
            status_code=400, detail="File must be an image (jpg, jpeg, png)"
        )
    try:
        return await predict_image_class(file)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Brain prediction failed for file=%s", file.filename)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
