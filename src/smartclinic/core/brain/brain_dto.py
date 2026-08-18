from __future__ import annotations

from pydantic import BaseModel, Field

from smartclinic.core.predict_labels import (
    MESSAGE_FIELD_DESCRIPTION,
    class_index_description,
)

_BRAIN_CLASS_SLUG = (
    "English class slug from class_indices.json (glioma, meningioma, notumor, pituitary)."
)


class PredictBrainResponse(BaseModel):
    prediction: int = Field(..., description=class_index_description("brain"))
    predicted_class: str = Field(..., description=_BRAIN_CLASS_SLUG)
    confidence: float = Field(
        ...,
        description="Softmax confidence as a percentage in [0, 100].",
        ge=0,
        le=100,
    )
    message: str = Field(..., description=MESSAGE_FIELD_DESCRIPTION)
