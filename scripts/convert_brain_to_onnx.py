#!/usr/bin/env python3
"""Convert brain Keras .h5 → ONNX. Keeps the original .h5 untouched.

One-time tooling (needs TensorFlow + tf2onnx). Runtime inference uses onnxruntime only.

Usage (from repo root):
  uv sync
  uv pip install 'tensorflow-cpu>=2.15' tf2onnx
  uv run python scripts/convert_brain_to_onnx.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H5_PATH = ROOT / "models/model_predict/brain/Tumor_classification_vgg16.h5"
ONNX_PATH = ROOT / "models/model_predict/brain/Tumor_classification_vgg16.onnx"
INPUT_SIZE = (240, 240)


def main() -> int:
    if not H5_PATH.exists():
        print(f"Missing source model: {H5_PATH}", file=sys.stderr)
        return 1

    try:
        import tensorflow as tf  # noqa: F401
        import tf2onnx
        from tensorflow.keras.models import load_model
    except ImportError as exc:
        print(
            "Conversion requires TensorFlow + tf2onnx (install only for this step):\n"
            "  uv pip install 'tensorflow-cpu>=2.15' tf2onnx\n"
            f"Detail: {exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Loading Keras model: {H5_PATH}")
    model = load_model(str(H5_PATH))

    spec = (
        tf.TensorSpec((None, INPUT_SIZE[0], INPUT_SIZE[1], 3), tf.float32, name="input"),
    )
    print(f"Exporting ONNX → {ONNX_PATH} (source .h5 kept)")
    tf2onnx.convert.from_keras(
        model,
        input_signature=spec,
        opset=13,
        output_path=str(ONNX_PATH),
    )
    print(f"Done. Size: {ONNX_PATH.stat().st_size / (1024 * 1024):.1f} MB")
    print(f"Original preserved: {H5_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
