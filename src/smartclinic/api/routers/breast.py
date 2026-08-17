from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.breast_cancer.breast_dto import (
    PredictBreastRequest,
    PredictBreastResponse,
)
from smartclinic.core.breast_cancer.breast_service import process_prediction

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict/breast_cancer", tags=["Breast Cancer Prediction"])
def predict(
    data: PredictBreastRequest,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
) -> PredictBreastResponse:
    try:
        prediction, message = process_prediction(data)
        return PredictBreastResponse(prediction=prediction, message=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Breast prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
