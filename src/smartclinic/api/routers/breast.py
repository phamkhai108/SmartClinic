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
from smartclinic.core.predict_labels import get_english_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/predict/breast_cancer",
    tags=["Breast Cancer Prediction"],
    response_model=PredictBreastResponse,
)
def predict(
    data: PredictBreastRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> PredictBreastResponse:
    """Predict breast-tumor class from morphology features.

    ``prediction`` class index:
        * ``0``: benign
        * ``1``: malignant

    ``message`` is the English label. Map ``prediction`` on the client for i18n.
    """
    try:
        prediction = int(process_prediction(data))
        logger.info("predict.breast user=%s prediction=%s", user.id, prediction)
        return PredictBreastResponse(
            prediction=prediction,
            message=get_english_message("breast", prediction),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Breast prediction failed user=%s", user.id)
        raise HTTPException(status_code=500, detail=str(e)) from e
