# Meerkat — Project Knowledge Base

## What it is
Meerkat is a **Social Commerce Command Center** — a web app for small business owners who sell through Facebook and Instagram. It unifies their seller experience: message inbox, sales tracking, and AI-generated sales strategy, all in one dashboard.

## Core problem it solves
Small sellers using Facebook Marketplace / Instagram Shopping currently juggle multiple separate apps (FB inbox, IG inbox, sales records) manually. Meta's own tools (Business Suite, the new Seller app) partially solve this but are either not PH-focused, not web-based, or don't offer AI-driven strategy recommendations.

## Core features (MVP scope)
1. **Registration/Auth** — sellers sign up using **Facebook Login for Business** (OAuth). This single flow covers both their Facebook Page and any connected Instagram Business account — there is no separate "Instagram login," IG access comes through the linked FB Page.
2. **Unified Inbox (read-only)** — dashboard shows a combined list of who messaged the seller today, tagged by platform (FB vs IG). Messages are ingested via Meta webhooks, not live polling.
   - Initial version is **read-only** — no reply-from-dashboard in MVP, though the same OAuth permissions (`pages_messaging`, `instagram_manage_messages`) technically grant send capability if that's added later.
3. **Sales tracking widget** — pulled from Meta Commerce/Catalog API and/or Insights endpoints (reach, clicks, profile views).
4. **AI Sales Strategy (differentiator)** — seller provides their **own LLM API key** (BYOK — OpenAI, Anthropic, or Gemini) in settings. A scheduled job aggregates their weekly Insights data (reach, clicks, message volume) into a prompt, calls their key, and renders a written strategy card in the dashboard (e.g. "Tuesday posts get 3x reach — consider posting drops then").
   - This is fully independent of Fritz's other project (Byokai) — no cross-product dependency.

## Explicitly ruled out
- **No reverse-engineered/unofficial API bridges** (e.g. Beeper-style account impersonation) — violates Meta's ToS, risks real seller account bans, and isn't something to build even from public repos.
- **TikTok messaging** — considered for later, but TikTok's official Business Messaging API is narrowly gated (Shop sellers / eligible regions only), not a general developer signup. Treated as a possible future addition, not MVP scope.

## Tech stack (final)
| Layer | Choice | Why |
|---|---|---|
| Backend | **FastAPI** (Python) | Async I/O for webhooks; best LLM SDK support (OpenAI/Anthropic/Gemini) for the AI strategy feature |
| Database | **PostgreSQL via Supabase** (free tier) | Persistent/non-expiring — avoids Render's free Postgres 30-day wipe |
| Queue/Jobs | **Redis + Celery** | Async webhook processing (ack Meta fast, process after) + scheduled weekly AI-strategy job (Celery Beat) |
| Frontend | **React + Server-Sent Events (SSE)** | Live-updating inbox/message-count widgets; one-directional server→client push is simpler than WebSockets here |
| Hosting | **Render** (free tier) — web service + worker + Key Value (Redis) | Free tier works for web service/worker; only Postgres needed to move to Supabase |
| Encryption | Python `cryptography` (Fernet) | Encrypt stored OAuth tokens and seller-provided LLM API keys at rest |

## Meta API permissions needed
- `pages_show_list`, `pages_read_engagement`, `pages_messaging`
- `instagram_basic`, `instagram_manage_messages`, `instagram_manage_insights`
- `catalog_management` (if pulling product/sales data via Commerce API)
- All of the above work freely in **Development Mode** (own account + up to 25 test users) at zero cost. Going live for real sellers requires **App Review** (demo video, privacy policy) and likely **Business Verification** for the sensitive permissions above.

## Cost model
- Entirely free-tier buildable: Graph API/Pages API/Messenger/Instagram messaging cost nothing to call, ever (policy-gated via the 24-hour messaging window + tags, not billed).
- WhatsApp Cloud API (not yet in MVP scope) is free within the customer-initiated 24h service window; paid templates only apply outside it — and starting Oct 1, 2026 even in-window messages start being charged, worth knowing if WhatsApp gets added later.

## The 24-hour messaging window (relevant if/when reply feature is added)
- Opens when a **customer** messages the Page/IG account.
- Resets only when the **customer** sends a new message — the seller replying does NOT extend it.
- Once closed, free-text replies aren't allowed without a Meta-approved message tag (e.g. `CONFIRMED_EVENT_UPDATE` for order status), which covers narrow legitimate use cases only.

## Repo structure
```
meerkat/
├── meerkat-frontend/   (Vite + React)
└── meerkat-backend/    (FastAPI, venv lives inside this folder)
```
- Opened as one VS Code workspace (parent `meerkat` folder).
- `.gitignore` should exclude `venv/`, `__pycache__/`, `*.pyc`, `.env`.

## Current status
- FastAPI backend and React frontend both scaffolded and confirmed talking to each other (CORS configured, test `/api/ping` endpoint returns successfully to the React app via `fetch`).
- Not yet built: Supabase connection, Meta Developer App registration, OAuth flow, webhook receiver, dashboard UI, SSE live updates, AI strategy pipeline.

## Agreed build order
1. Supabase Postgres connection in FastAPI (SQLAlchemy) — get one test table working first.
2. Organize backend into `main.py` / `database.py` / `models.py` / `routes/`.
3. Register Meta Developer App (Development Mode first — free, no approval needed yet). Start this early since App Review has a lead time.
4. Build Facebook Login for Business OAuth flow — first real feature, since everything else depends on a logged-in seller with a connected account.
5. Webhook receiver — verify Meta's signature, queue via Redis, process with Celery, store in `messages` table.
6. Dashboard UI — start with a simple message list, then layer in SSE for live updates.
7. AI strategy feature (BYOK) — last, since it depends on Insights data already being collected.

## Project name origin
"Meerkat" — chosen for the metaphor of meerkats living in social groups with lookouts that constantly watch for activity, fitting the real-time multi-channel inbox concept.

## Coding Style & Commenting Rules
When adding or modifying code, agents must strictly follow these commenting rules:
1. **Headers / Main Code Blocks**: Use the comment symbol followed by ` ======== ` and ALL CAPS followed by ` =======`.
   - Example (JS/TS): `// ======== DATABASE CONNECTION =======`
   - Example (Python): `# ======== DATABASE CONNECTION =======`
2. **Sub-code / Line-by-line**: Add comments for every logical line/step. These must be entirely in lowercase with no punctuation (no periods) at the end.
   - Example (JS/TS): `// getting the info on db`
   - Example (Python): `# getting the info on db`
3. **Comment Content**: Comments must describe what the code does using short text only, while still providing the needed important details. Keep it concise but meaningful.
4. **Plain English**: Use very simple, plain English. Avoid deep or overly technical jargon. The main goal is to make it easy for anyone to understand exactly what the code is doing.