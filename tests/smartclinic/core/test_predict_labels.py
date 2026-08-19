from __future__ import annotations

import pytest

from smartclinic.core.brain.brain_dto import PredictBrainResponse
from smartclinic.core.breast_cancer.breast_dto import PredictBreastResponse
from smartclinic.core.heart.heart_dto import PredictResponseDto
from smartclinic.core.lung.lung_dto import PredictLungResponse
from smartclinic.core.predict_labels import (
    BRAIN_MESSAGES,
    BREAST_MESSAGES,
    HEART_MESSAGES,
    LUNG_MESSAGES,
    PredictModel,
    class_index_description,
    get_english_message,
)


@pytest.mark.parametrize(
    ("model", "prediction", "expected"),
    [
        ("heart", 0, "No heart failure symptoms"),
        ("heart", 1, "Heart failure symptoms"),
        ("lung", 0, "No cancer risk when age is 0"),
        ("lung", 1, "Low cancer risk"),
        ("lung", 2, "Moderate cancer risk"),
        ("lung", 3, "High cancer risk"),
        ("breast", 0, "Benign"),
        ("breast", 1, "Malignant"),
        ("brain", 0, "glioma"),
        ("brain", 1, "meningioma"),
        ("brain", 2, "notumor"),
        ("brain", 3, "pituitary"),
    ],
)
def test_get_english_message_known_classes(model: str, prediction: int, expected: str):
    assert get_english_message(model, prediction) == expected


def test_get_english_message_unknown_class():
    assert get_english_message("heart", 9) == "Unknown class 9"


def test_get_english_message_unknown_model():
    with pytest.raises(ValueError, match="Unknown predict model"):
        get_english_message("kidney", 0)


@pytest.mark.parametrize("model", ["heart", "lung", "breast", "brain"])
def test_class_index_description_lists_all_classes(model: PredictModel):
    desc = class_index_description(model)
    assert desc.startswith("Class index.")
    mapping = {
        "heart": HEART_MESSAGES,
        "lung": LUNG_MESSAGES,
        "breast": BREAST_MESSAGES,
        "brain": BRAIN_MESSAGES,
    }[model]
    for idx, label in mapping.items():
        assert f"{idx}={label}" in desc


def test_brain_registry_matches_canonical_indices():
    assert BRAIN_MESSAGES == {
        0: "glioma",
        1: "meningioma",
        2: "notumor",
        3: "pituitary",
    }


def test_response_dto_schema_documents_class_index():
    heart = PredictResponseDto.model_json_schema()["properties"]["prediction"]
    lung = PredictLungResponse.model_json_schema()["properties"]["prediction"]
    breast = PredictBreastResponse.model_json_schema()["properties"]["prediction"]
    brain = PredictBrainResponse.model_json_schema()["properties"]
    assert "0=" in heart["description"]
    assert "1=Low cancer risk" in lung["description"]
    assert "1=Malignant" in breast["description"]
    assert "0=glioma" in brain["prediction"]["description"]
    assert "class_indices.json" in brain["predicted_class"]["description"]
    assert HEART_MESSAGES and LUNG_MESSAGES and BREAST_MESSAGES
