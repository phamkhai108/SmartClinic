# AI Chat

[← Guides index](README.md)

---

## What this is for

A conversational assistant that helps staff ask clinical or operational questions quickly.  
When an Admin has uploaded internal documents and search is configured, answers can include **source document names**.

---

## When it works well

| Condition | If missing |
| --- | --- |
| Signed in | Redirected to sign-in |
| LLM configured in `.env` | Chat unavailable |
| Vector store + embedding + Admin uploads | Chat still works, but **without** (or with fewer) internal document sources |

See: [setup](setup.md) · [Admin — upload documents](admin-guide.md)

---

## How to use

1. Sign in → open **AI Chat**.
2. Start a new conversation or open a previous session.
3. Type a clear clinical / operational question → Send.
4. Read the streamed reply; if present, review the **Sources** tags (files retrieved for that answer).

### Screenshot — Chat overview

<!-- Add screenshot: sidebar + conversation -->

![AI Chat](./images/03-chat.png)

> Save as `doc/images/03-chat.png`

### Screenshot — Answer with sources

<!-- Add screenshot: Sources tags under a reply -->

![Chat with sources](./images/03b-chat-sources.png)

> Save as `doc/images/03b-chat-sources.png`

### Screenshot — Session history

<!-- Add screenshot: session list -->

![Chat sessions](./images/03c-chat-sessions.png)

> Save as `doc/images/03c-chat-sessions.png`

---

## Good practice

- Ask specific questions (context, symptoms, which policy or document area).
- Always **verify** against source documents and clinical judgment.
- Do not enter patient-identifying data unless your organization allows it in this system.

Next: [Clinical screening](clinical-prediction.md) · UI: [frontend/doc/chat.md](../frontend/doc/chat.md)
