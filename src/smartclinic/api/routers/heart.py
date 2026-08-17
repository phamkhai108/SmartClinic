from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.heart.heart_dto import (
    PredictHeartRequestDto,
    PredictResponseDto,
)
from smartclinic.core.heart.heart_service import process_prediction

router = APIRouter()


@router.post("/predict/heart_failure", tags=["Heart Failure Prediction"])
def predict(
    data: PredictHeartRequestDto,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    try:
        prediction = process_prediction(data)
        result = (
            "Triệu chứng suy tim" if prediction == 1 else "Không mắc triệu chứng suy tim"
        )
        return PredictResponseDto(
            prediction=prediction,
            message=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
