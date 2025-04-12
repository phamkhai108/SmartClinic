from pydantic import BaseModel


class PredictBrainResponse(BaseModel):
    predicted_class: str
    confidence: float
