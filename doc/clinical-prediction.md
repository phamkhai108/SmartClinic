# Clinical screening

[← Guides index](README.md)

---

## What this is for

Structured **risk screening / classification** from form data or MRI images.  
Results support triage and discussion — they are **not** a final diagnosis.

| Module | Who can use | Main input |
| --- | --- | --- |
| Heart failure | User · Doctor · Admin | Clinical form |
| Lung cancer | User · Doctor · Admin | Risk / symptom form |
| Breast cancer | User · Doctor · Admin | Morphology feature form |
| Brain tumor (MRI) | **Doctor · Admin** | JPG or PNG image |

---

## Form-based modules (heart / lung / breast)

1. Sign in → open the relevant screening item in the menu.
2. Complete the form (validation errors appear if fields are missing or invalid).
3. Submit → review the **Results** screen (label / risk level and charts when available).
4. Use the outcome for clinical discussion — not as a standalone diagnosis.

### Screenshot — Example form (heart failure)

<!-- Add screenshot -->

![Heart failure form](./images/04-predict-heart.png)

> Save as `doc/images/04-predict-heart.png`

### Screenshot — Results

<!-- Add screenshot -->

![Screening result](./images/05-predict-result.png)

> Save as `doc/images/05-predict-result.png`

Optional additional shots:

![Lung form](./images/04b-predict-lung.png)

![Breast form](./images/04c-predict-breast.png)

---

## Brain MRI classification

Only **Doctor** and **Admin** can open this module.

### Steps

1. Open **Brain** / MRI screening.
2. Select a JPG or PNG image (respect the size limit shown in the UI).
3. Submit → review predicted class and confidence.

### Screenshot — Upload MRI

<!-- Add screenshot -->

![Brain MRI upload](./images/06-predict-brain.png)

> Save as `doc/images/06-predict-brain.png`

### Screenshot — Classification result

<!-- Add screenshot -->

![Brain result](./images/06b-predict-brain-result.png)

> Save as `doc/images/06b-predict-brain-result.png`

---

## If a module is unavailable

Usually a model file is missing under `models/` (or brain `.onnx` was not converted) — see [setup §6](setup.md#6-prediction-models-optional-note). Other modules keep working.

Next: [Admin](admin-guide.md) · UI: [frontend/doc/prediction.md](../frontend/doc/prediction.md)
