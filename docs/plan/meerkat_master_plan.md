# Meerkat — Master Project Plan

> **What is Meerkat?**
> A web app that gives small Filipino sellers on Facebook and Instagram one place to see all their customer messages, track their sales numbers, and get AI-powered tips on how to sell better.

---

## What We Have Already Built

These are the parts of the project that are finished and working today.

| # | What | Status | Where in the Code |
|---|------|--------|-------------------|
| 1 | **Project setup** — Backend (FastAPI) and Frontend (React + Vite) scaffolded, talking to each other | ✅ Done | `main.py`, `App.jsx` |
| 2 | **Database connection** — Supabase Postgres connected via SQLAlchemy | ✅ Done | `database.py` |
| 3 | **Database tables** — Sellers table, Messages table, and a test table | ✅ Done | `models.py` |
| 4 | **Token encryption** — Encrypt/decrypt seller access tokens at rest using Fernet | ✅ Done | `security.py` |
| 5 | **Facebook Login for Business** — Seller clicks a button, logs into Facebook, grants permissions, and their token is saved encrypted in the database | ✅ Done | `routes/auth.py` |
| 6 | **Auto page subscription** — After login, the backend automatically tells Meta to start forwarding messages for the seller's Facebook Pages | ✅ Done | `routes/auth.py` |
| 7 | **Webhook receiver** — Meta sends us real-time messages, we verify the signature, parse the message, and save it to the database | ✅ Done | `routes/webhooks.py` |
| 8 | **Deployment** — Backend deployed on Render, frontend deployed on Render, database on Supabase | ✅ Done | `.env.render` files |
| 9 | **End-to-end test** — Sent a real Facebook message to a test Page, confirmed it arrived in the Supabase `messages` table | ✅ Done | — |

### Open Items (Not Blocking, But Need Doing)
- **Instagram DM support** — Code is written but Meta Dashboard still needs the IG permissions configured and a test account set up. Tracked in [GitHub Issue #8](https://github.com/Frehitzz/Meerkat/issues/8).
- **CORS fix for deployed frontend** — The backend needs to allow the live Render frontend URL. Code is written locally but not yet pushed.

---

## The MVP — What We Still Need to Build

The MVP is the simplest version of Meerkat that a real seller could actually use. It has four screens and one background job. Everything below is listed in the order we should build it.

---

### Phase 6: Dashboard UI — The Unified Inbox

> **Goal:** The seller logs in and sees a list of all the messages people sent to their Facebook Page and Instagram account, all in one place.

**What the seller sees:**
- A clean login screen with a "Login with Facebook" button
- After login, a dashboard with a sidebar showing their name and connected pages
- A message list showing: sender name, message text, platform tag (FB or IG), and when it was sent
- Messages sorted newest first
- A simple filter to show "All", "Facebook only", or "Instagram only"

**What we need to build:**

| Task | Layer | Details |
|------|-------|---------|
| `GET /api/messages` endpoint | Backend | Returns all messages for the logged-in seller, newest first. Supports filtering by platform |
| `GET /api/me` endpoint | Backend | Returns the current seller's profile info (name, connected pages) so the frontend knows who is logged in |
| Session/auth middleware | Backend | A way for the frontend to prove who the seller is on every request (JWT token or session cookie) |
| Login page | Frontend | Clean, professional login screen with Facebook button |
| Dashboard layout | Frontend | Sidebar + main content area |
| Message list component | Frontend | Shows messages with platform tags, sender info, and timestamps |
| Platform filter | Frontend | Toggle between All / Facebook / Instagram |

**Done when:** A seller can log in, see their real Facebook messages on screen, and filter by platform.

---

### Phase 7: Live Updates with SSE

> **Goal:** When a new message arrives, it pops up on the dashboard instantly without the seller needing to refresh the page.

**What the seller sees:**
- They are looking at the dashboard
- Someone sends a message to their Facebook Page
- The message appears at the top of the list within 1-2 seconds, with a subtle animation
- A small notification badge shows the count of new unread messages

**What we need to build:**

| Task | Layer | Details |
|------|-------|---------|
| SSE endpoint (`GET /api/messages/stream`) | Backend | Keeps a connection open and pushes new messages to the frontend in real time |
| Hook webhook to SSE | Backend | When a webhook saves a new message, it also pushes it through the SSE stream |
| EventSource listener | Frontend | Listens to the SSE stream and adds new messages to the list without refreshing |
| New message animation | Frontend | Smooth fade-in or slide-in when a new message appears |
| Unread badge | Frontend | Small counter showing how many new messages arrived since last check |

**Done when:** A seller is on the dashboard, someone messages their Page, and the message appears on screen within seconds.

---

### Phase 8: Sales Tracking Widget

> **Goal:** The seller sees basic numbers about how their Facebook Page and Instagram account are doing — reach, clicks, profile views, and message volume.

**What the seller sees:**
- A "Sales Overview" card on the dashboard
- Numbers like: "This week: 1,200 people reached, 45 link clicks, 12 new conversations"
- A simple bar chart or line graph showing trends over the past 4 weeks
- Data updates daily

**What we need to build:**

| Task | Layer | Details |
|------|-------|---------|
| `GET /api/insights` endpoint | Backend | Pulls reach, impressions, clicks, and profile views from Meta's Page Insights API and Instagram Insights API |
| Insights data model | Backend | A table to cache daily insights so we don't re-fetch from Meta every time |
| Daily insights job | Backend | A scheduled task that pulls fresh insights data once a day |
| Insights card component | Frontend | Clean card showing key numbers with labels |
| Simple chart | Frontend | A lightweight chart (bar or line) showing weekly trends |
| Message volume counter | Backend | Count messages per day from the existing `messages` table |

**Done when:** The seller sees real numbers from their Facebook/Instagram account on the dashboard, updated daily.

---

### Phase 9: AI Sales Strategy (The Differentiator)

> **Goal:** The seller gets a weekly written strategy card powered by AI, based on their actual sales data. The seller brings their own API key (OpenAI, Anthropic, or Gemini).

**What the seller sees:**
- A "Settings" page where they can paste their own LLM API key and pick a provider (OpenAI, Anthropic, or Gemini)
- A "Strategy" card on the dashboard with a written recommendation like:
  - *"Your Tuesday posts get 3x more reach than other days. Consider scheduling your product drops on Tuesdays at 7pm."*
  - *"You received 8 messages about pricing this week but only 2 led to sales. Consider adding prices directly to your posts."*
- The strategy refreshes once a week automatically

**What we need to build:**

| Task | Layer | Details |
|------|-------|---------|
| Settings page | Frontend | Form where seller enters their LLM API key and picks a provider |
| `POST /api/settings/llm-key` endpoint | Backend | Saves the seller's encrypted LLM API key in the database |
| LLM key model | Backend | Add an `encrypted_llm_key` and `llm_provider` column to the Seller table |
| Strategy prompt builder | Backend | Takes the seller's weekly insights data and message volume, turns it into a clear prompt |
| LLM caller | Backend | Sends the prompt to the right provider (OpenAI / Anthropic / Gemini) using the seller's own key |
| Weekly strategy job | Backend | Runs once a week (Celery Beat), generates a strategy for each seller who has a key saved |
| Strategy card component | Frontend | Displays the latest AI strategy on the dashboard |
| Strategy history | Backend | Store past strategies so the seller can look back at previous weeks |

**Done when:** A seller with a saved API key sees a fresh AI-written strategy card on their dashboard every week, based on their real data.

---

## After MVP — The Big Picture

These are ideas for after the MVP is shipped and working. They are not committed — just possibilities ranked by how much value they add.

### Tier 1: High Value, Build Soon After MVP

| Feature | What It Does | Why It Matters |
|---------|-------------|----------------|
| **Reply from dashboard** | Seller can type a reply to a customer directly from Meerkat instead of switching to Facebook/Instagram | Saves massive time for sellers who get 50+ messages a day |
| **Multi-account support** | One seller can connect multiple Facebook Pages and IG accounts | Many sellers run 2-3 shops across different pages |
| **Mobile-friendly dashboard** | Make the dashboard work great on phones | Most Filipino sellers manage their shops from their phones |

### Tier 2: Medium Value, Nice to Have

| Feature | What It Does | Why It Matters |
|---------|-------------|----------------|
| **Customer profiles** | Group messages by customer — see all past conversations with one person | Helps sellers remember repeat buyers |
| **Quick replies / templates** | Pre-saved reply templates like "Thanks for your order!" | Speeds up repetitive responses |
| **Order tagging** | Seller can tag a conversation as "Inquiry", "Sold", "Shipped" | Simple sales pipeline tracking |
| **Daily digest email** | Email summary every morning: "You got 12 new messages yesterday, 3 sales" | Keeps sellers informed even when they don't open the app |

### Tier 3: Future Exploration

| Feature | What It Does | Why It Matters |
|---------|-------------|----------------|
| **TikTok Shop integration** | Pull TikTok messages into the unified inbox | Expanding to a third platform, but TikTok API access is very limited right now |
| **WhatsApp Business integration** | Pull WhatsApp messages into the inbox | Many PH sellers also use WhatsApp, but messaging costs money after Oct 2026 |
| **Team access** | Multiple people can log into one seller account with different roles | For sellers who have assistants handling messages |
| **Product catalog sync** | Show the seller's Facebook/IG product catalog inside Meerkat | Useful for seeing which products get the most inquiries |

---

## Technical Debt to Clean Up Along the Way

These are not features, but things we should fix as we go to keep the codebase healthy.

| Item | Why |
|------|-----|
| **Remove test endpoints** | `POST /api/test-db` and `GET /api/test-db` in `main.py` were for initial testing and should be removed |
| **Add Redis + Celery** | Right now webhooks are processed directly in the request. We should acknowledge Meta instantly and process in the background via a queue |
| **Add proper auth middleware** | The frontend currently has no way to prove who the seller is after login. We need JWT or session-based auth |
| **Update AGENTS.md "Current status"** | The status section still says "Not yet built: Supabase connection..." but most of that is done now |
| **Error handling** | Add proper try/catch blocks and logging throughout the backend so errors are easy to debug |
| **Rate limiting** | Add basic rate limiting to public endpoints to prevent abuse |

---

## Quick Reference: Build Order

```
✅ Phase 1: Environment & Secrets         — DONE
✅ Phase 2: Database & Token Security      — DONE
✅ Phase 3: Facebook Login (OAuth)         — DONE
✅ Phase 4: Webhook Receiver               — DONE
✅ Phase 5: Testing & Deployment           — DONE
⬜ Phase 6: Dashboard UI (Unified Inbox)   — NEXT
⬜ Phase 7: Live Updates (SSE)
⬜ Phase 8: Sales Tracking Widget
⬜ Phase 9: AI Sales Strategy (BYOK)
```

---

*Last updated: August 12, 2026*
