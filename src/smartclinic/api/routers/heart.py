from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.heart.heart_dto import (
    PredictHeartRequestDto,
    PredictResponseDto,
)
from smartclinic.core.heart.heart_service import process_prediction
from smartclinic.core.predict_labels import get_english_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/predict/heart_failure",
    tags=["Heart Failure Prediction"],
    response_model=PredictResponseDto,
)
def predict(
    data: PredictHeartRequestDto,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> PredictResponseDto:
    """Predict heart-failure class from clinical features.

    ``prediction`` class index:
        * ``0``: no heart failure symptoms
        * ``1``: heart failure symptoms

    ``message`` is the English label. Map ``prediction`` on the client for i18n.
    """
    try:
        prediction = int(process_prediction(data))
        logger.info("predict.heart user=%s prediction=%s", user.id, prediction)
        return PredictResponseDto(
            prediction=prediction,
            message=get_english_message("heart", prediction),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Heart prediction failed user=%s", user.id)
        raise HTTPException(status_code=500, detail=str(e)) from e
