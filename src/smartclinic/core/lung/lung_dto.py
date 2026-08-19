from __future__ import annotations

from pydantic import BaseModel, Field

from smartclinic.core.predict_labels import (
    MESSAGE_FIELD_DESCRIPTION,
    class_index_description,
)


class PredictLung(BaseModel):
    Age: int
    Gender: int
    Air_Pollution: int
    Alcohol_use: int
    OccuPational_Hazards: int
    Genetic_Risk: int
    chronic_Lung_Disease: int
    Smoking: int
    Passive_Smoker: int
    Chest_Pain: int
    Coughing_of_Blood: int
    Clubbing_of_Finger_Nails: int


class PredictLungResponse(BaseModel):
    prediction: int = Field(..., description=class_index_description("lung"))
    message: str = Field(..., description=MESSAGE_FIELD_DESCRIPTION)
