from fastapi import APIRouter, HTTPException

from smartclinic.core.heart.heart_dto import (
    ChestPainTypeEnum,
    ExerciseAnginaEnum,
    RestingECGEnum,
    SexEnum,
    STSlopeEnum,
)
from smartclinic.core.heart.heart_service import PredictData, process_prediction

router = APIRouter()
@router.get("/predict/heart_failure", tags=["Heart Failure Prediction"])
def predict(
    Age: int,
    Sex: SexEnum,
    ChestPainType: ChestPainTypeEnum,
    RestingBP: int,
    Cholesterol: int,
    FastingBS: int,
    RestingECG: RestingECGEnum,
    MaxHR: int,
    ExerciseAngina: ExerciseAnginaEnum,
    Oldpeak: float,
    ST_Slope: STSlopeEnum
):
    try:
        input_data = PredictData(
            Age=Age,
            Sex=Sex,
            ChestPainType=ChestPainType,
            RestingBP=RestingBP,
            Cholesterol=Cholesterol,
            FastingBS=FastingBS,
            RestingECG=RestingECG,
            MaxHR=MaxHR,
            ExerciseAngina=ExerciseAngina,
            Oldpeak=Oldpeak,
            ST_Slope=ST_Slope
        )
        prediction = process_prediction(input_data)
        if prediction == 1:
            result = "Triệu chứng suy tim"
        else:
            result = "Không mắc triệu chứng suy tim"
        return {"prediction": int(prediction), "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))