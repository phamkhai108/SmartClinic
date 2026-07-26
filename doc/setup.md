# Setup — Backend

[← Guides index](README.md)

Prepare your machine, fill `.env`, then start the API so the web app (or other clients) can connect.

---

## 1. What you need

| Item | Required? | Notes |
| --- | --- | --- |
| Python ≥ 3.11 | Yes | Check with `python --version` |
| [uv](https://github.com/astral-sh/uv) | Yes | Installs dependencies and runs the API |
| `.env` file | Yes | Copy from `.env.example` |
| Docker | Optional | Only if you enable Elasticsearch or Milvus (document search) |
| LLM (OpenAI-compatible, e.g. Ollama) | Optional | Required for **AI Chat** |
| Embedding endpoint | Optional | Required for **document upload / search** (may differ from the LLM host) |
| Email (Gmail app password) | Optional | Required for **self-service registration** (OTP) |

Without LLM, vector DB, or mail, other features (demo login, predictions when models are present) can still run.

---

## 2. Install

```bash
# From the SmartClinic repository root (includes the default `dev` group)
uv sync
uv run pre-commit install
```

Pre-commit runs Ruff lint (`--fix`) then format on staged Python files. Check everything once:

```bash
uv run pre-commit run --all-files
```

### Before push / CI

Same checks as `.github/workflows/ci.yml`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

---

## 3. Configure `.env`

```bash
cp .env.example .env
```

### 3.1 Required — the app will not start without these

```env
SMARTCLINIC_DATABASE_URL=sqlite:///./example.db
SMARTCLINIC_JWT_SECRET=replace-with-a-long-random-secret
```

| Variable | Purpose |
| --- | --- |
| `SMARTCLINIC_DATABASE_URL` | Users, files, chat history (SQLite is fine for local trials) |
| `SMARTCLINIC_JWT_SECRET` | Signs login sessions — use ≥ 16 characters |

### 3.2 Optional — AI Chat (LLM)

```env
SMARTCLINIC_LLM_API_URL=http://localhost:11434/v1
SMARTCLINIC_LLM_API_KEY=ollama
SMARTCLINIC_MODEL_LLM_ID=your-chat-model
```

### 3.3 Optional — Embedding (upload & document search)

May use a **different** host or model than the LLM:

```env
SMARTCLINIC_EMBED_API_URL=http://localhost:11434/v1
SMARTCLINIC_EMBED_API_KEY=ollama
SMARTCLINIC_MODEL_EMBED_ID=your-embedding-model
```

The embedding model must produce **1536**-dimension vectors to match the vector store.

### 3.4 Optional — Document store (vector database)

Choose **one** backend (data is not synced between them):

**Elasticsearch**

```env
SMARTCLINIC_VECTOR_BACKEND=elasticsearch
SMARTCLINIC_ES_HOST=http://localhost:9200
```

```bash
docker compose -f docker/elastic.yaml up -d
```

**Milvus**

```env
SMARTCLINIC_VECTOR_BACKEND=milvus
SMARTCLINIC_MILVUS_URI=http://localhost:19530
```

```bash
docker compose -f docker/milvus.yaml up -d
```

### 3.5 Optional — Registration email

```env
SMARTCLINIC_SENDER_EMAIL=you@gmail.com
SMARTCLINIC_SENDER_PASSWORD=gmail-app-password
```

### 3.6 CORS (local UI)

```env
SMARTCLINIC_CORS_ORIGINS=http://localhost:5173,http://localhost:5000
```

---

## 4. Start the API

```bash
uv run uvicorn smartclinic.api.main:app --reload --app-dir src --port 8000
```

| URL | Meaning |
| --- | --- |
| http://localhost:8000/health | Service is up |
| http://localhost:8000/docs | Interactive API docs (optional) |

---

## 5. Demo accounts

When the database is empty, these accounts are created:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@example.com` | `admin` |
| Doctor | `doctor@gmail.com` | `doctor` |

Then start the UI: [frontend/doc/setup.md](../frontend/doc/setup.md).

---

## 6. Prediction models (optional note)

- Tabular models (heart / lung / breast) live under `models/`.
- Brain MRI uses an `.onnx` file. If missing, convert once (temporary TensorFlow install):

```bash
uv pip install 'tensorflow-cpu>=2.15' tf2onnx
uv run python scripts/convert_brain_to_onnx.py
```

If a model is missing, only that screening module is unavailable — the rest of the product keeps working.

---

## Next

- [Sign in & registration](login-register.md)
- [Frontend setup](../frontend/doc/setup.md)
