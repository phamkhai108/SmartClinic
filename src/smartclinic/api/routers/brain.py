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
    user: Annotated[CurrentUser, Depends(require_roles("doctor", "admin"))],
    file: Annotated[UploadFile, File()],
) -> PredictBrainResponse:
    """Classify brain MRI into a tumor class.

    ``prediction`` class index:
        * ``0``: glioma
        * ``1``: meningioma
        * ``2``: notumor
        * ``3``: pituitary

    ``predicted_class`` and ``message`` are the English slug. Map ``prediction``
    on the client for i18n. ``confidence`` is a percentage in ``[0, 100]``.
    """
    if not file.filename or not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(
            status_code=400, detail="File must be an image (jpg, jpeg, png)"
        )
    try:
        result = await predict_image_class(file)
        logger.info(
            "predict.brain user=%s prediction=%s confidence=%s",
            user.id,
            result.prediction,
            result.confidence,
        )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Brain prediction failed user=%s file=%s", user.id, file.filename
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
