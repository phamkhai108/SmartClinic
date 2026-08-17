from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.deps_auth import CurrentUser, get_current_user
from smartclinic.core.lung.lung_dto import PredictLung
from smartclinic.core.lung.lung_service import process_prediction

router = APIRouter()


@router.post("/predict/lung_cancer", tags=["Lung Cancer Prediction"])
def predict(
    data: PredictLung,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    try:
        prediction, message = process_prediction(data)
        return {"prediction": prediction, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
