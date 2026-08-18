from __future__ import annotations

from typing import Final, Literal

PredictModel = Literal["heart", "lung", "breast", "brain"]

MESSAGE_FIELD_DESCRIPTION: Final[str] = (
    "English prediction label for this class. Clients should map `prediction` for i18n."
)

HEART_MESSAGES: Final[dict[int, str]] = {
    0: "No heart failure symptoms",
    1: "Heart failure symptoms",
}

LUNG_MESSAGES: Final[dict[int, str]] = {
    0: "No cancer risk when age is 0",
    1: "Low cancer risk",
    2: "Moderate cancer risk",
    3: "High cancer risk",
}

BREAST_MESSAGES: Final[dict[int, str]] = {
    0: "Benign",
    1: "Malignant",
}

BRAIN_MESSAGES: Final[dict[int, str]] = {
    0: "glioma",
    1: "meningioma",
    2: "notumor",
    3: "pituitary",
}

MESSAGES: Final[dict[str, dict[int, str]]] = {
    "heart": HEART_MESSAGES,
    "lung": LUNG_MESSAGES,
    "breast": BREAST_MESSAGES,
    "brain": BRAIN_MESSAGES,
}


def class_index_description(model: PredictModel) -> str:
    mapping = MESSAGES[model]
    parts = "; ".join(f"{idx}={label}" for idx, label in sorted(mapping.items()))
    return f"Class index. {parts}."


def get_english_message(model: str, prediction: int) -> str:
    labels = MESSAGES.get(model)
    if labels is None:
        raise ValueError(f"Unknown predict model: {model}")
    return labels.get(prediction, f"Unknown class {prediction}")
