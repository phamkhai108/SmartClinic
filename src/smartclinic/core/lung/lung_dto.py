from pydantic import BaseModel


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