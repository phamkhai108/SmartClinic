# Admin guide

[← Guides index](README.md)

---

## Who uses this?

**Admin** only.  
Main jobs: overview dashboard, manage users, **upload documents** for AI Chat, and manage the document library.

---

## Before document upload works

1. Vector database + embedding configured in `.env` ([setup](setup.md)).
2. Elasticsearch or Milvus is running.
3. Files are one of: PDF, DOCX, XLSX, PPTX, Markdown.

Upload is accepted immediately (`pending`), then processed in the background until `success` or `failed`. You can follow status on the Files page.

---

## Admin dashboard

1. Sign in as Admin.
2. Open **Admin**.
3. Use summary cards and shortcuts to Users / Files / Upload.

### Screenshot — Dashboard

<!-- Add screenshot -->

![Admin dashboard](./images/07-admin-dashboard.png)

> Save as `doc/images/07-admin-dashboard.png`

---

## Upload documents (feeds Chat RAG)

### Steps

1. Open **Upload**.
2. Select the **owner user** for the document metadata.
3. Choose a supported file → submit.
4. Wait for background indexing (large files may take longer). The UI may show “processing” until finished.
5. Confirm status under **Files** (`success` or `failed`).

### Screenshot — Upload form

<!-- Add screenshot -->

![Admin upload](./images/08-admin-upload.png)

> Save as `doc/images/08-admin-upload.png`

### Screenshot — Processing / success

<!-- Add screenshot -->

![Upload success](./images/08b-admin-upload-ok.png)

> Save as `doc/images/08b-admin-upload-ok.png`

---

## Document library

1. Open **Files**.
2. Filter by user or view all (as available in the UI).
3. Delete documents that are no longer needed — associated search content is removed as well.

### Screenshot — File list

<!-- Add screenshot -->

![File list](./images/09-admin-files.png)

> Save as `doc/images/09-admin-files.png`

---

## User management

1. Open **Users**.
2. Change roles between **User** and **Doctor** when MRI access is required.
3. Admin elevation is not a routine UI action — follow your internal process.

### Screenshot — Users & role change

<!-- Add screenshot -->

![User management](./images/10-admin-users.png)

> Save as `doc/images/10-admin-users.png`

---

## Suggested operating checklist

- [ ] Admin uploaded the clinic’s standard document set  
- [ ] Test Chat with a question that should cite those documents  
- [ ] Doctor role granted only to staff who need MRI screening  
- [ ] Demo passwords changed  

UI walkthrough: [frontend/doc/admin.md](../frontend/doc/admin.md)
