# SmartClinic

A medical diagnosis support system: FastAPI backend + Vue 3 frontend.

## Requirements

- Python ≥ 3.11, [uv](https://github.com/astral-sh/uv)
- Node.js ≥ 20
- (Optional) Elasticsearch, Ollama/OpenAI-compatible LLM

## Configuration

Copy `.env.example` to `.env` and fill in the required values.

| Group   | Variables                                                       | Behavior if Missing                                                                                       |
| ------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Core    | `SMARTCLINIC_DATABASE_URL`, `SMARTCLINIC_JWT_SECRET`            | The application **will not start**                                                                        |
| Mail    | `SENDER_*`                                                      | Registration / email features return HTTP 503                                                             |
| RAG/LLM | `VECTOR_BACKEND`, `ES_HOST` / `MILVUS_*`, `OPENAI_*`, `MODEL_*` | Search/upload returns HTTP 503; chat only requires an LLM                                                 |
| Models  | Files in `models/`                                              | Prediction endpoints return HTTP 503; brain prediction requires an `.onnx` model (see conversion section) |

`setup_db` always uses `SMARTCLINIC_DATABASE_URL` (no hardcoded `example.db`). Admin and doctor accounts are seeded only when the `users` table is empty.

### Vector Database (Elasticsearch | Milvus)

Choose **one** backend (data is **not synchronized** between them). Vector dimension = **1536**.

| Backend                 | Environment Variables                                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Elasticsearch (default) | `SMARTCLINIC_VECTOR_BACKEND=elasticsearch` + `SMARTCLINIC_ES_HOST=http://localhost:9200`                                      |
| Milvus                  | `SMARTCLINIC_VECTOR_BACKEND=milvus` + `SMARTCLINIC_MILVUS_URI=http://localhost:19530` (+ optional `SMARTCLINIC_MILVUS_TOKEN`) |

```bash
# Elasticsearch
docker compose -f docker/elastic.yaml up -d

# Milvus (+ Attu UI :8800)
docker compose -f docker/milvus.yaml up -d
```

If an old Elasticsearch `chunks` index still uses dimension 384, delete the index, restart the API (it will recreate the index with dimension 1536), and re-upload the documents.

## Backend

```bash
uv sync
uv run uvicorn smartclinic.api.main:app --reload --app-dir src --port 8000
```

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Test Accounts

| Role   | Email               | Password |
| ------ | ------------------- | -------- |
| admin  | `admin@example.com` | `admin`  |
| doctor | `doctor@gmail.com`  | `doctor` |

The seed process only runs when the `users` table is empty (fresh database). If the admin account already exists, use the credentials above (they are reset when necessary).

- **Admin**: access `/admin` (users, files, upload)
- **Doctor/Admin**: upload Brain MRI images at `/app/predict/brain`

### Prediction Endpoints (JWT Required)

- `POST /predict/heart_failure`
- `POST /predict/lung_cancer`
- `POST /predict/breast_cancer`
- `POST /brain/predict_tumor` (doctor/admin only) — inference is performed using **ONNX Runtime** (CPU). If the `.onnx` model is missing, the endpoint returns HTTP 503.

### Brain Model: Convert `.h5` → `.onnx` (One-Time Only)

Keep the original `Tumor_classification_vgg16.h5` file. Runtime inference uses the `.onnx` model because it is significantly lighter than TensorFlow on CPU.

```bash
# From the project root directory
# TensorFlow is only required for conversion, not for running the API
uv pip install 'tensorflow-cpu>=2.15' tf2onnx
uv run python scripts/convert_brain_to_onnx.py
```

Output files:

- Original model (keep): `models/model_predict/brain/Tumor_classification_vgg16.h5`
- Inference model: `models/model_predict/brain/Tumor_classification_vgg16.onnx`

After conversion, restart the API and test `/app/predict/brain`.

If desired, you can remove the conversion tools afterward:

```bash
uv pip uninstall tensorflow-cpu tf2onnx
```

(`onnxruntime` will remain installed through `uv sync`.)

### Upload / Ingestion (Docling)

- `POST /files/upload_flow` — Admin only; documents are parsed using **Docling** `DocumentConverter`
- Chunking: **HierarchicalChunker** + `contextualize()` → embeddings (1536 dimensions) → vector store
- Supported formats: PDF, DOCX, XLSX, PPTX, Markdown
- Module: `core/ingestion/` (`ingest_controller` → `ingest_service`)
- `File.status`: `pending` → `success` | `failed`

### Chat (LangChain Agent + SSE)

- `POST /chat_all/chat` — `text/event-stream` only (JWT required)
- Chat **only requires an LLM**. Vector search (`search_documents`) is optional and depends on the configured `VECTOR_BACKEND` (Elasticsearch or Milvus) plus an embedding model.
- If both a vector store and embedding model are available, the agent automatically enables a search tool (top 4 retrieved documents). If vector search is unavailable or fails, the agent still responds normally (no HTTP 503).
- SSE Events:
    - `token`
    - `references`
    - `done`
    - `error`
- If no LLM is configured, the API returns HTTP **503** (`MISSING_CONFIG`).

## Frontend (Vue 3)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

By default, the frontend uses:

```
VITE_API_BASE_URL=http://localhost:8000
```

### Main Routes

- `/`, `/about`, `/login`, `/register`
- `/app/chat`
- `/app/predict/{heart,lung,breast,brain}` + `/result`
- `/admin`, `/admin/users`, `/admin/files`, `/admin/upload`

### Tech Stack

Vue 3 · Vite · TypeScript · Vue Router · Pinia · Naive UI · Tailwind CSS · Axios · VeeValidate + Zod · Vue I18n (vi/en) · ECharts · markdown-it

### User Roles

- `user` / `doctor`: Chat, Heart, Lung, Breast prediction
- `doctor` / `admin`: Brain MRI prediction
- `admin`: User management, File management, Upload, Search

## Frontend Docker

```bash
docker build -t smartclinic-ui ./frontend --build-arg VITE_API_BASE_URL=http://localhost:8000
docker run -p 8080:80 smartclinic-ui
```

The legacy `UI/` directory (static HTML) is temporarily retained. The primary user interface is located in the `frontend/` directory.
