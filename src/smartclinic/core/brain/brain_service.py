import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

from smartclinic.common.errors import feature_unavailable_error
from smartclinic.core.brain.brain_dto import PredictBrainResponse

_SESSION = None
_INPUT_NAME: str | None = None
_CLASS_LABELS: dict[int, str] | None = None

_INPUT_SIZE = (240, 240)


def _project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "models" / "model_predict" / "brain"
        if candidate.is_dir():
            return parent
    return Path.cwd()


def _brain_dir() -> Path:
    return _project_root() / "models" / "model_predict" / "brain"


def _onnx_path() -> Path:
    return _brain_dir() / "Tumor_classification_vgg16.onnx"


def _labels_path() -> Path:
    return _brain_dir() / "class_indices.json"


def _load_session():
    global _SESSION, _INPUT_NAME, _CLASS_LABELS
    if _SESSION is not None and _CLASS_LABELS is not None and _INPUT_NAME is not None:
        return _SESSION, _INPUT_NAME, _CLASS_LABELS

    onnx_path = _onnx_path()
    labels_path = _labels_path()

    if not onnx_path.exists():
        raise feature_unavailable_error(
            "Brain ONNX model missing. Convert with: "
            "uv pip install 'tensorflow-cpu>=2.15' tf2onnx && "
            "uv run python scripts/convert_brain_to_onnx.py",
            code="MISSING_MODEL",
        )
    if not labels_path.exists():
        raise feature_unavailable_error(
            "Brain tumor label file is missing.",
            code="MISSING_MODEL",
        )

    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise feature_unavailable_error(
            "onnxruntime is not installed; brain prediction unavailable.",
            code="MISSING_DEPENDENCY",
        ) from exc

    _SESSION = ort.InferenceSession(
        str(onnx_path),
        providers=["CPUExecutionProvider"],
    )
    _INPUT_NAME = _SESSION.get_inputs()[0].name
    with open(labels_path) as f:
        class_indices = json.load(f)
    _CLASS_LABELS = {int(v): k for k, v in class_indices.items()}
    return _SESSION, _INPUT_NAME, _CLASS_LABELS


def _preprocess(contents: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img = img.resize(_INPUT_SIZE)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


async def predict_image_class(file) -> PredictBrainResponse:
    session, input_name, class_labels = _load_session()
    contents = await file.read()
    batch = _preprocess(contents)

    outputs = session.run(None, {input_name: batch})
    predictions = np.asarray(outputs[0][0], dtype=np.float32)
    predicted_class_idx = int(np.argmax(predictions))
    confidence = float(predictions[predicted_class_idx])

    return PredictBrainResponse(
        predicted_class=class_labels[predicted_class_idx],
        confidence=round(confidence * 100, 2),
    )
