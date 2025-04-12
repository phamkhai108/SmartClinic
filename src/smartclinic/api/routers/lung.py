from fastapi import APIRouter, HTTPException

from smartclinic.core.lung.lung_dto import PredictLung
from smartclinic.core.lung.lung_service import process_prediction

router = APIRouter()


@router.post("/predict/lung_cancer", tags=["Lung Cancer Prediction"])
def predict(data: PredictLung):
    try:
        prediction, message = process_prediction(data)
        return {"prediction": prediction, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
how to use this endpoint:
curl -X POST http://localhost:8000/predict/lung_cancer \
  -H "Content-Type: application/json" \
  -d '{
        "Age": 60,
        "Gender": 1,
        "Air_Pollution": 3,
        "Alcohol_use": 2,
        "OccuPational_Hazards": 1,
        "Genetic_Risk": 2,
        "chronic_Lung_Disease": 1,
        "Smoking": 2,
        "Passive_Smoker": 1,
        "Chest_Pain": 2,
        "Coughing_of_Blood": 1,
        "Clubbing_of_Finger_Nails": 1
      }'


"""
