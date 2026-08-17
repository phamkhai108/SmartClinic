# Sign in & registration

[← Guides index](README.md)

---

## Who uses this?

Anyone who needs Chat AI or clinical screening must sign in.  
New self-registered accounts receive the **User** role. Doctor and Admin accounts are granted by your organization (or use the demo accounts after first setup).

---

## Sign in

### Steps

1. Open the web app (typically http://localhost:5173).
2. Choose **Sign in**.
3. Enter **email** and **password**.
4. On success you enter the workspace (usually AI Chat).

### Screenshot — Sign-in page

<!-- Add screenshot: sign-in form -->

![Sign-in page](./images/01-login.png)

> Save as `doc/images/01-login.png`

### Screenshot — After successful sign-in

<!-- Add screenshot: first screen after login -->

![After sign-in](./images/01b-after-login.png)

> Save as `doc/images/01b-after-login.png`

### Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@example.com` | `admin` |
| Doctor | `doctor@gmail.com` | `doctor` |

*(Only when the database was empty at first start — see [setup](setup.md).)*

---

## Register a new account

Requires email OTP configuration in `.env` (see [setup §3.5](setup.md#35-optional--registration-email)).

### Steps

1. Open **Register**.
2. Enter name, email, and password → send verification code.
3. Check email for the **6-digit code**.
4. Complete registration → sign in with the new account.

### Screenshot — Registration (step 1)

<!-- Add screenshot: registration form -->

![Registration step 1](./images/02-register.png)

> Save as `doc/images/02-register.png`

### Screenshot — Enter OTP (step 2)

<!-- Add screenshot: OTP field -->

![Registration OTP](./images/02b-register-otp.png)

> Save as `doc/images/02b-register-otp.png`

---

## Business notes

- Wrong password or unverified email blocks access.
- To grant Doctor privileges, an **Admin** changes the role in Admin → Users.
- Sign out on shared workstations.

Next: [AI Chat](chat-ai.md) · UI walkthrough: [frontend/doc/login.md](../frontend/doc/login.md)
