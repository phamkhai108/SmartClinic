# SmartClinic

**AI-assisted clinical decision support** for care teams — faster risk screening and instant answers from your clinic’s own documents.

[![Python](https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/UI-Vue%203-42b883)](https://vuejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Outputs are **assistive only**. Final clinical decisions remain with licensed professionals.

---

## What SmartClinic offers

| Capability | Who it’s for |
| --- | --- |
| AI chat grounded in **internal clinic documents** | Signed-in staff |
| Risk screening: heart failure, lung cancer, breast cancer | User · Doctor · Admin |
| Brain tumor classification from MRI images | Doctor · Admin |
| User management and document ingestion for the knowledge base | Admin |

---

## Guides

| Need | Open |
| --- | --- |
| Prepare environment & run the API | **[doc/setup.md](doc/setup.md)** |
| Run the web app | **[frontend/doc/setup.md](frontend/doc/setup.md)** |
| How to use each feature (with screenshot placeholders) | **[doc/](doc/README.md)** · **[frontend/doc/](frontend/doc/README.md)** |

---

## Quick start

1. Install [uv](https://github.com/astral-sh/uv), Python ≥ 3.11, and Node.js ≥ 20  
2. Follow **[Backend setup](doc/setup.md)** (`.env` + start the API)  
3. Follow **[Frontend setup](frontend/doc/setup.md)**  
4. Open http://localhost:5173 and sign in  

**Demo accounts** (created only when the database is empty):

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@example.com` | `admin` |
| Doctor | `doctor@gmail.com` | `doctor` |

Change these passwords before any shared or production use.

---

## Roles at a glance

| Role | Can do |
| --- | --- |
| **User** | Chat AI; heart / lung / breast screening |
| **Doctor** | Everything a User can do, plus brain MRI classification |
| **Admin** | Everything above, plus users, document upload, and file management |

---

## License

[MIT License](LICENSE) — © 2025 phamkhai108

*SmartClinic supports diagnosis — it does not replace a physician.*
