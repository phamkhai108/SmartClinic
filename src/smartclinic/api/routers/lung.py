from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.lung.lung_dto import PredictLung, PredictLungResponse
from smartclinic.core.lung.lung_service import process_prediction
from smartclinic.core.predict_labels import get_english_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/predict/lung_cancer",
    tags=["Lung Cancer Prediction"],
    response_model=PredictLungResponse,
)
def predict(
    data: PredictLung,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> PredictLungResponse:
    """Predict lung-cancer risk class from lifestyle and clinical features.

    ``prediction`` class index:
        * ``0``: no cancer risk when age is 0
        * ``1``: low cancer risk
        * ``2``: moderate cancer risk
        * ``3``: high cancer risk

    ``message`` is the English label. Map ``prediction`` on the client for i18n.
    """
    try:
        prediction = int(process_prediction(data))
        logger.info("predict.lung user=%s prediction=%s", user.id, prediction)
        return PredictLungResponse(
            prediction=prediction,
            message=get_english_message("lung", prediction),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Lung prediction failed user=%s", user.id)
        raise HTTPException(status_code=500, detail=str(e)) from e
