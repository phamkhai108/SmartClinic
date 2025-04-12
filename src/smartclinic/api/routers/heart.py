from fastapi import APIRouter, HTTPException

from smartclinic.core.heart.heart_dto import (
    PredictHeartRequestDto,
    PredictResponseDto,
)
from smartclinic.core.heart.heart_service import process_prediction

router = APIRouter()


@router.post("/predict/heart_failure", tags=["Heart Failure Prediction"])
def predict(data: PredictHeartRequestDto):
    try:
        prediction = process_prediction(data)
        result = (
            "Triệu chứng suy tim" if prediction == 1 else "Không mắc triệu chứng suy tim"
        )
        return PredictResponseDto(
            prediction=prediction,
            message=result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
how to use:
curl -X POST http://localhost:8000/predict/heart_failure \
  -H "Content-Type: application/json" \
  -d '{
    "Age": 45,
    "Sex": "M",
    "ChestPainType": "ATA",
    "RestingBP": 130,
    "Cholesterol": 250,
    "FastingBS": 0,
    "RestingECG": "Normal",
    "MaxHR": 160,
    "ExerciseAngina": "N",
    "Oldpeak": 1.5,
    "ST_Slope": "Up"
}'
"""
