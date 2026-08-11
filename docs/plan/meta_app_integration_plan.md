# Meta App Integration Plan

## Overview
This document outlines the step-by-step plan to integrate the newly created Meta Developer App into the Meerkat backend and frontend. The setup focuses on the three selected Meta use cases:
1. **Messenger Integration** (`pages_messaging`, `pages_show_list`, `pages_read_engagement`)
2. **Instagram Integration** (`instagram_basic`, `instagram_manage_messages`)
3. **Catalog & Insights API** (`catalog_management` / `/insights`)

---

## Plan Roadmap

### Phase 1: Environment & Secrets Configuration
- **Objective**: Store sensitive credentials safely without hardcoding them in the repository.
- **Tasks**:
  1. Add Meta App credentials to `meerkat-backend/.env`:
     - `META_APP_ID`
     - `META_APP_SECRET`
     - `META_WEBHOOK_VERIFY_TOKEN` (custom string for webhook handshake)
     - `ENCRYPTION_KEY` (Fernet secret key for token encryption)
  2. Update `.env.example` to document these new environment variables.

---

### Phase 2: Database Schema & Token Security
- **Objective**: Prepare PostgreSQL (Supabase) to store seller data and encrypted access tokens.
- **Tasks**:
  1. Define the `Seller` model in `meerkat-backend/models.py`:
     - `id`: Primary key
     - `facebook_user_id`: Unique identifier from Meta
     - `name`: Seller's name
     - `encrypted_access_token`: Fernet-encrypted long-lived Meta token
     - `created_at`: Timestamp
  2. Implement helper utilities in `meerkat-backend/security.py` using `cryptography.fernet` to encrypt and decrypt access tokens at rest.

---

### Phase 3: Facebook Login for Business (OAuth Flow)
- **Objective**: Allow sellers to log in and authorize Meerkat to access their FB Pages and Instagram Business DMs.
- **Tasks**:
  1. **Backend OAuth Endpoints** (`meerkat-backend/routes/auth.py`):
     - `GET /api/auth/facebook`: Constructs the Meta OAuth authorization URL requesting permissions (`pages_messaging`, `instagram_manage_messages`, `pages_show_list`, `pages_read_engagement`).
     - `GET /api/auth/facebook/callback`:
       - Handles Meta's authorization code response.
       - Exchanges short-lived code for a long-lived access token via Graph API.
       - Encrypts the access token and saves/updates the seller record in PostgreSQL.
  2. **Frontend Login UI** (`meerkat-frontend`):
     - Add a "Login with Facebook for Business" button on the UI that redirects the seller to `/api/auth/facebook`.

---

### Phase 4: Meta Webhook Receiver (Live Messaging Ingestion)
- **Objective**: Receive real-time Messenger and Instagram DMs directly from Meta.
- **Tasks**:
  1. **Webhook Handshake Endpoint**:
     - `GET /api/webhook`: Responds to Meta's hub verification request (`hub.mode`, `hub.challenge`, `hub.verify_token`).
  2. **Webhook Message Receiver**:
     - `POST /api/webhook`:
       - Verifies Meta request signature (`X-Hub-Signature-256`) to ensure authentic requests.
       - Acknowledges Meta immediately with `200 OK`.
       - Hands off message payloads to Redis/Celery queue for async parsing into the `messages` database table.

---

### Phase 5: Verification & Testing in Development Mode
- **Objective**: Ensure the pipeline works end-to-end using Meta Development Mode.
- **Tasks**:
  1. Test OAuth login flow with a Facebook test user or admin account.
  2. Use Meta's Webhook Simulator / ngrok tunnel to test live Messenger and IG DM webhook events.
  3. Verify encrypted tokens in Supabase.
