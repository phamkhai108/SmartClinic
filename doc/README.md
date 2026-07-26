# User guides — SmartClinic

Business-oriented guides: prepare the system, then use each feature day to day.  
For step-by-step UI screens (with screenshot slots), see [frontend/doc/](../frontend/doc/README.md).

Back to: [Product README](../README.md)

---

## Quick links

| Guide | Contents |
| --- | --- |
| [Setup](setup.md) | Prerequisites, `.env`, start the API and optional services |
| [Sign in & registration](login-register.md) | First access and account creation |
| [AI Chat](chat-ai.md) | Clinical Q&A over internal documents |
| [Clinical screening](clinical-prediction.md) | Heart, lung, breast, and brain MRI |
| [Admin](admin-guide.md) | Users, document upload, file library |

---

## Adding screenshots

Each feature guide includes **Screenshot** placeholders with suggested file names.  
Save images under [`images/`](images/README.md) using those names (or update the markdown paths).

Example:

```markdown
![Sign-in page](./images/01-login.png)
```

---

## Important notes

- Results **support** decisions; they do not replace clinical judgment.
- Change demo passwords before use outside a personal machine.
- Document-grounded chat is useful only after an Admin has uploaded documents and LLM + vector search are configured — see [setup](setup.md).
- Document upload is accepted immediately, then indexed in the background (`pending` → `success` / `failed`).
