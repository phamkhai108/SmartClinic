from __future__ import annotations

from pydantic import BaseModel


class PredictBrainResponse(BaseModel):
    predicted_class: str
    confidence: float
