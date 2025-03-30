from fastapi import APIRouter, Depends, HTTPException

from smartclinic.core.lung.lung_dto import PredictLung
from smartclinic.core.lung.lung_service import process_prediction

router = APIRouter()
@router.get("/predict/lung_cancer", tags=["Lung Cancer Prediction"])
def predict(data: PredictLung = Depends()):  # noqa: B008
    try:
        prediction, message = process_prediction(data)
        return {"prediction": prediction, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))