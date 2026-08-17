# Phase 6 — Session & Auth Middleware: Secure Seller Authentication

> **Overview:**
> **NOW:** The frontend only knows who the seller is because the backend passed seller details in the URL query string (?seller_id=1&seller_name=Harly), and anyone can query GET /api/messages without proving their identity.
> **AFTER THIS FEATURE:** The backend generates a signed JWT session token upon Facebook login. The frontend stores this token and sends it in the Authorization: Bearer <token> header with every API request. A FastAPI dependency validates the token, protects endpoints, and guarantees that sellers can only access their own data.

---

## 🧠 Before We Code: Understanding the Concepts

### What is a JWT Session Token?

**Analogy:** Imagine entering an exclusive private club or music festival.
1. When you first arrive at the entrance, you show your government ID / ticket (**Facebook Login**).
2. The security guard verifies your ID and gives you a stamped, tamper-proof **wristband** (**JWT Token**).
3. Every time you order food, enter the lounge, or request service (**API Requests**), you just show your wristband. The staff doesn't need to call the entrance gate every time — they just check the wristband's stamp.

**In Technical Terms:**
* A **JSON Web Token (JWT)** is a digitally signed string containing the seller's ID and an expiration timestamp.
* When the backend issues it, it signs it with a secret server key.
* The frontend includes this token in the Authorization: Bearer <token> header on every request.
* If someone tampers with the token, the backend's signature check fails and immediately rejects the request with 401 Unauthorized.

---

### The Full Flow for This Feature

```text
1. Seller clicks "Login with Facebook"
       │
       ▼ (already works)
2. Facebook authenticates seller & redirects to backend callback
       │
       ▼ (NEW — Step 1 & 2)
3. Backend creates JWT session token for seller & redirects to frontend with token
       │
       ▼ (NEW — Step 3)
4. Frontend saves JWT in localStorage & calls GET /api/auth/me with Bearer token
       │
       ▼ (NEW — Step 4 & 5)
5. Backend auth dependency verifies JWT signature & returns seller profile
       │
       ▼ (NEW — Step 6)
6. Frontend attaches Bearer token to GET /api/messages to fetch protected inbox
       │
       ▼
7. Secure dashboard loaded 🎉
```


*Steps 1–2 already exist. We are building steps 3–7 in this tutorial.*

---

## Now Let's Build It! 🔨

---

## Step 1: Install PyJWT and Configure JWT Secret

**What is this?**
We need PyJWT in our Python backend to create and verify signed JWT tokens.

1. Add `pyjwt` to `meerkat-backend/requirements.txt`:

```text
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
pytest
httpx
ruff
cryptography
pyjwt
```

2. Install dependencies in backend virtualenv:
```powershell
cd meerkat-backend
.\venv\Scripts\pip install pyjwt
```

3. Update `meerkat-backend/.env.example` and `meerkat-backend/.env` with `JWT_SECRET`:
```ini
JWT_SECRET=super_secret_jwt_key_change_me_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=168
```


---

## Step 2: Create JWT Helper Functions in `security.py`

**What is this?**
We add functions to create a signed JWT token when a seller logs in, and decode/verify that token when a request comes in.

Open `meerkat-backend/security.py` and add the JWT functions:

```python
import os
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from dotenv import load_dotenv
import jwt

# ======== LOAD ENV =======
# read hidden variables from environment
load_dotenv()

# ======== ENCRYPTION SETUP =======
# get secret key from hidden environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "meerkat_dev_jwt_secret_key_12345")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "168"))

# check if key exists
if ENCRYPTION_KEY:
    # build encryption tool using key
    fernet = Fernet(ENCRYPTION_KEY.encode())
else:
    # create temporary key if running in test environment
    _fallback_key = Fernet.generate_key()
    # build encryption tool using fallback key
    fernet = Fernet(_fallback_key)

# ======== ENCRYPT TOKEN =======
# function to lock secret token safely
def encrypt_token(token: str) -> str:
    # change text token into encrypted bytes and return string
    return fernet.encrypt(token.encode()).decode()

# ======== DECRYPT TOKEN =======
# function to unlock secret token
def decrypt_token(encrypted_token: str) -> str:
    # decrypt text token using key and return clean string
    return fernet.decrypt(encrypted_token.encode()).decode()

# ======== CREATE JWT SESSION TOKEN =======
# create signed jwt session token for seller
def create_access_token(seller_id: int) -> str:
    # calculate expiration time
    expire_time = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    # build payload dictionary
    payload = {
        "sub": str(seller_id),
        "exp": expire_time,
        "iat": datetime.now(timezone.utc),
    }
    # sign token with jwt secret and algorithm
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ======== VERIFY JWT SESSION TOKEN =======
# verify and decode seller id from jwt token
def decode_access_token(token: str) -> int | None:
    try:
        # decode and verify token signature
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # return seller id integer
        return int(payload.get("sub"))
    except (jwt.PyJWTError, ValueError, TypeError):
        # return none if token is invalid or expired
        return None
```

#### `create_access_token(seller_id: int)`
Generates a signed JWT containing the seller's ID in the `sub` (subject) claim and an expiration date 7 days into the future.

#### `decode_access_token(token: str)`
Verifies the cryptographic signature using `JWT_SECRET`. If the token is modified or expired, it safely returns `None`.

---

## Step 3: Create FastAPI Auth Middleware Dependency

**What is this?**
We need a reusable dependency (`get_current_seller`) that intercepts incoming API requests, extracts the `Authorization: Bearer <token>` header, verifies the token, and provides the logged-in `Seller` object to route handlers.

Create a new file `meerkat-backend/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import database
import models
import security

# ======== BEARER SCHEME SETUP =======
# set up http bearer token extractor
bearer_scheme = HTTPBearer(auto_error=False)

# ======== GET CURRENT SELLER =======
# dependency that gets authenticated seller from bearer token
def get_current_seller(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(database.get_db),
) -> models.Seller:
    # check if authorization header is missing
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # decode seller id from jwt token
    seller_id = security.decode_access_token(credentials.credentials)
    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # find seller in database
    seller = db.query(models.Seller).filter_by(id=seller_id).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # return authenticated seller object
    return seller
```

---

## Step 4: Update OAuth Callback & Add `GET /api/auth/me`

**What is this?**
1. Update `facebook_callback` in `routes/auth.py` to generate the JWT token and include `token=<jwt>` in the redirect.
2. Add `GET /api/auth/me` so the frontend can query the seller's profile with its token.

Open `meerkat-backend/routes/auth.py` and update:

```python
from dependencies import get_current_seller
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse

# ... (inside facebook_callback)

    # create jwt session token for seller
    session_token = security.create_access_token(seller.id)

    # build query parameters to pass session token and seller info back to frontend
    query_params = urlencode({
        "auth": "success",
        "token": session_token,
        "seller_id": seller.id,
        "seller_name": seller.name,
        "fb_user_id": seller.facebook_user_id,
    })

    # redirect seller browser back to frontend dashboard page
    return RedirectResponse(url=f"{frontend_url}/?{query_params}")

# ======== GET AUTHENTICATED SELLER PROFILE =======
# link to get currently logged in seller profile
@router.get("/me")
def get_current_seller_profile(seller: models.Seller = Depends(get_current_seller)):
    # send back seller profile details
    return {
        "id": seller.id,
        "name": seller.name,
        "facebook_user_id": seller.facebook_user_id,
    }
```

---

## Step 5: Protect the Messages Endpoint

**What is this?**
Update `GET /api/messages` in `meerkat-backend/routes/messages.py` to require `seller: models.Seller = Depends(get_current_seller)`.

Open `meerkat-backend/routes/messages.py` and update:

```python
from dependencies import get_current_seller
from fastapi import Depends
from sqlalchemy.orm import Session
import database
import models

@router.get("")
def get_messages(
    platform: str = "all",
    db: Session = Depends(database.get_db),
    seller: models.Seller = Depends(get_current_seller),
):
    # query messages with optional platform filter
    query = db.query(models.Message).filter(models.Message.seller_id == seller.id)
    if platform != "all":
        query = query.filter(models.Message.platform == platform)

    messages = query.order_by(models.Message.created_at.desc()).all()
    # format and return list
    return [
        {
            "id": m.id,
            "platform": m.platform.value if hasattr(m.platform, "value") else str(m.platform),
            "sender_id": m.sender_id,
            "sender_name": m.sender_name,
            "sender_profile_pic": m.sender_profile_pic,
            "recipient_id": m.recipient_id,
            "message_text": m.message_text,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]
```

---

## Step 6: Update Frontend Storage & API Calls

**What is this?**
1. When redirecting from login, save `token` to `localStorage`.
2. Send `Authorization: Bearer <token>` in `fetch` headers inside `DashboardView.jsx` and `App.jsx`.
3. If any API call returns `401 Unauthorized`, automatically log out and redirect to the landing page.

In `meerkat-frontend/src/App.jsx`:
* Parse `token` from URL parameters and save `localStorage.setItem("token", token)`.
* On app mount, if `token` exists in `localStorage`, call `GET /api/auth/me` with `Authorization: Bearer <token>` to verify session validity.

In `meerkat-frontend/src/DashboardView.jsx`:
* Update `fetchMessages`:
```javascript
const token = localStorage.getItem("token");
const response = await fetch(url, {
  headers: {
    "Authorization": token ? `Bearer ${token}` : "",
  },
});
if (response.status === 401) {
  onLogout();
  return;
}
```

---

## Step 7: Test It Manually

1. Start both servers:
   ```powershell
   .\run_all.ps1
   ```
2. Open `http://localhost:5173` in your browser.
3. Open DevTools (F12) → **Application** tab → **Local Storage**.
4. Click **Login with Facebook for Business**.
5. Once logged in, verify:
   * `token` is stored in Local Storage (starts with `ey...`).
   * In DevTools **Network** tab, click `GET /api/messages` and verify request headers contain `Authorization: Bearer ey...`.
   * Messages load properly with status `200 OK`.
6. Test unauthorized rejection:
   * In DevTools console, run:
     ```javascript
     fetch('http://localhost:8000/api/messages').then(r => console.log(r.status))
     ```
   * Verify it returns `401 Unauthorized`.
7. Click **Logout**:
   * Verify `token` is cleared from `localStorage`.
   * Verify the UI returns to the clean login screen.

---

## Step 8: Write Automated Tests

Add backend tests in `meerkat-backend/test_main.py`:
1. `test_access_token_creation_and_decoding`: Tests JWT generation and decoding.
2. `test_get_me_endpoint_with_valid_token`: Tests `GET /api/auth/me` returns seller info when a valid token is provided.
3. `test_get_me_endpoint_unauthorized`: Tests `GET /api/auth/me` returns `401` when token is missing or invalid.
4. `test_get_messages_unauthorized`: Tests `GET /api/messages` returns `401` without token.
5. `test_get_messages_authorized`: Tests `GET /api/messages` returns `200` with valid Bearer token.

Run backend test suite:
```powershell
cd meerkat-backend
.\venv\Scripts\pytest
.\venv\Scripts\ruff check .
```

Run frontend test suite:
```powershell
cd meerkat-frontend
npm run lint
npm run test:run
```

---

## ✅ Session/Auth Middleware Checklist

- [ ] Add `pyjwt` to `requirements.txt` and install in venv
- [ ] Implement `create_access_token` & `decode_access_token` in `security.py`
- [ ] Create `dependencies.py` with `get_current_seller`
- [ ] Add `GET /api/auth/me` and update OAuth redirect in `routes/auth.py`
- [ ] Protect `GET /api/messages` in `routes/messages.py`
- [ ] Update frontend `App.jsx` and `DashboardView.jsx` to store and send Bearer tokens
- [ ] Add backend and frontend automated tests
- [ ] 100% pass on pytest, ruff, eslint, and vitest

---

## 🔮 What's Next? (Phase 7: Live Updates with SSE)

Once every request is securely tied to the authenticated seller via JWT, we can build the **Server-Sent Events (SSE)** endpoint (`GET /api/messages/stream`) in Phase 7. The SSE connection will authenticate using the same session token, allowing the server to push new Facebook and Instagram customer messages in real time without refreshing!
