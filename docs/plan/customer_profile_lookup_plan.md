# Phase 6 Extension — Customer Profile Lookup: Resolving Real Customer Names & Avatars

> **Before:** When a customer messages the Facebook Page, Meta only sends a raw numerical Page-Scoped ID (PSID) like `235048192837`. The dashboard falls back to displaying `User #235048`.
>
> **After:** Meerkat automatically queries the Meta Graph API using the Page access token to fetch the customer's real name (e.g., "Maria Santos") and profile picture, caching it in the database and displaying it on the dashboard.

---

## 🧠 Before We Code: Understanding the Concepts

### What is a Page-Scoped ID (PSID)?

Imagine going to a large building where the front desk gives you a numbered visitor badge (`Visitor #235048`). The badge number is unique to that specific building — if you go to a different building across the street, they give you a completely different visitor badge number.

In Facebook Messenger:
- When a customer messages a Facebook Page, Meta **does not** give the Page their global Facebook ID or personal profile URL for privacy reasons.
- Instead, Meta creates a **Page-Scoped ID (PSID)** that is unique only to the relationship between that customer and that specific Facebook Page.
- Webhook payloads only deliver this PSID (`sender.id`) and the message text.

### How Do We Get the Customer's Real Name?

To get the customer's actual name and profile picture from their PSID, we ask Meta's Graph API:

```http
GET https://graph.facebook.com/v19.0/{PSID}?fields=first_name,last_name,profile_pic&access_token={PAGE_ACCESS_TOKEN}
```

Meta returns:
```json
{
  "first_name": "Maria",
  "last_name": "Santos",
  "profile_pic": "https://platform-lookaside.fbsbx.com/platform/profilepic/...",
  "id": "235048192837"
}
```

---

### The Full Flow for This Feature

```
1. Customer sends message to Facebook Page
       │
       ▼ (already works)
2. Meta webhook delivers payload with sender PSID & message text
       │
       ▼ (NEW — Step 1: Check database or call Graph API)
3. Backend looks up PSID:
   - If customer profile already exists in DB → use cached name
   - If new customer → call Meta Graph API `/{PSID}` with Page token
       │
       ▼ (NEW — Step 2: Save message with sender name)
4. Backend saves message with `sender_name` & `sender_profile_pic` in DB
       │
       ▼ (NEW — Step 3: Serve data to Frontend)
5. `GET /api/messages` returns `sender_name` & `sender_profile_pic`
       │
       ▼ (NEW — Step 4: UI display)
6. Dashboard renders "Maria Santos" and their profile avatar 🎉
```

> *Steps 1–2 already exist. We are building steps 3–6 in this plan.*

---

## Now Let's Build It! 🔨

---

## Step 1: Update the Database Model

**What is this?**
We need to store the customer's display name and profile picture URL in the `messages` table so we don't have to call Meta Graph API on every single message.

1. Open `meerkat-backend/models.py` and add `sender_name` and `sender_profile_pic` columns to the `Message` model:

```python
# ======== MESSAGE MODEL =======
# create the blueprint for incoming social messages
class Message(database.Base):
    # set the name of the table in the database
    __tablename__ = "messages"

    # make a unique id number for each message
    id = Column(Integer, primary_key=True, index=True)
    # store platform type using our enum
    platform = Column(Enum(Platform), index=True)
    # store sender id from meta (psid)
    sender_id = Column(String, index=True)
    # store customer real display name (NEW)
    sender_name = Column(String, nullable=True)
    # store customer profile photo url (NEW)
    sender_profile_pic = Column(String, nullable=True)
    # store recipient page or account id
    recipient_id = Column(String, index=True)
    # store message text body
    message_text = Column(String)
    # save date and time message arrived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Step 2: Create a Meta Graph API Profile Lookup Helper

**What is this?**
A dedicated helper function that takes the `sender_id` (PSID) and the `page_access_token`, requests the user profile from Meta Graph API, and handles errors gracefully.

1. Create or add a helper inside `meerkat-backend/routes/webhooks.py`:

```python
# ======== FETCH CUSTOMER PROFILE =======
# get customer name and profile image from meta graph api
async def fetch_customer_profile(sender_psid: str, access_token: str) -> dict:
    # return empty if missing credentials
    if not sender_psid or not access_token:
        return {}

    # graph api profile endpoint
    url = f"https://graph.facebook.com/v19.0/{sender_psid}"
    params = {
        "fields": "first_name,last_name,name,profile_pic",
        "access_token": access_token,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                first_name = data.get("first_name", "")
                last_name = data.get("last_name", "")
                full_name = data.get("name") or f"{first_name} {last_name}".strip()
                return {
                    "name": full_name or None,
                    "profile_pic": data.get("profile_pic"),
                }
    except Exception:
        pass

    return {}
```

---

## Step 3: Update Webhook Ingestion to Resolve and Save Names

**What is this?**
When a message webhook arrives in `routes/webhooks.py`:
1. Check if we already have a previous message from this `sender_id` with a known `sender_name`.
2. If not cached, look up the seller access token to call `fetch_customer_profile`.
3. Save `sender_name` and `sender_profile_pic` along with the message.

In `meerkat-backend/routes/webhooks.py`:

```python
# check if message text exists
if "text" in message_obj:
    sender_psid = sender.get("id", "")
    recipient_page_id = recipient.get("id", "")
    
    # check if we already have this customer name in database
    existing_msg = (
        db.query(models.Message)
        .filter(models.Message.sender_id == sender_psid, models.Message.sender_name.isnot(None))
        .first()
    )
    
    sender_name = existing_msg.sender_name if existing_msg else None
    sender_pic = existing_msg.sender_profile_pic if existing_msg else None

    # if customer name is not cached, attempt graph api lookup
    if not sender_name:
        # find seller owning this page to get page token
        seller = db.query(models.Seller).first()
        if seller and seller.encrypted_access_token:
            token = security.decrypt_token(seller.encrypted_access_token)
            profile = await fetch_customer_profile(sender_psid, token)
            sender_name = profile.get("name")
            sender_pic = profile.get("profile_pic")

    # create new message record with resolved name
    msg = models.Message(
        platform="facebook",
        sender_id=sender_psid,
        sender_name=sender_name,
        sender_profile_pic=sender_pic,
        recipient_id=recipient_page_id,
        message_text=message_obj.get("text", ""),
    )
    db.add(msg)
```

---

## Step 4: Update Backend `GET /api/messages` API Output

**What is this?**
Ensure the JSON output includes `sender_name` and `sender_profile_pic` for the frontend.

In `meerkat-backend/routes/messages.py`:

```python
# send back list of messages
return {
    "status": "success",
    "count": len(messages),
    "messages": [
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
    ],
}
```

---

## Step 5: Update Frontend Dashboard to Display Customer Name & Avatar

**What is this?**
In `DashboardView.jsx`, display the customer's real name `chat.sender_name` and show their avatar image if present, falling back to `User #235048` if no name is available yet.

1. In conversation grouping logic:
```javascript
groupMap.set(convKey, {
  id: convKey,
  sender_id: msg.sender_id,
  sender_name: msg.sender_name,
  sender_profile_pic: msg.sender_profile_pic,
  platform: msg.platform,
  recipient_id: msg.recipient_id,
  created_at: msg.created_at,
  snippet: msg.message_text,
  messages: [],
});
```

2. In Left Sidebar conversation list:
```jsx
<span className="text-[13px] font-semibold text-white truncate max-w-[170px]">
  {chat.sender_name || (chat.sender_id ? `User #${chat.sender_id.slice(-6)}` : "Customer")}
</span>
```

3. In Center Chat Header:
```jsx
<div className="flex items-center gap-3">
  {activeChat?.sender_profile_pic ? (
    <img
      src={activeChat.sender_profile_pic}
      alt="Avatar"
      className="w-8 h-8 rounded-full object-cover"
    />
  ) : (
    <div
      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
        activeChat?.platform === "facebook" ? "bg-[#1877f2]" : "bg-[#e1306c]"
      }`}
    >
      {activeChat?.sender_name
        ? activeChat.sender_name.charAt(0).toUpperCase()
        : activeChat?.sender_id?.charAt(0).toUpperCase() || "C"}
    </div>
  )}
  <div className="flex flex-col">
    <span className="text-sm font-semibold text-white">
      {activeChat?.sender_name || (activeChat?.sender_id ? `User #${activeChat.sender_id}` : "Customer")}
    </span>
    <span className="text-[11px] text-[#a1a1aa]">
      via {activeChat?.platform === "facebook" ? "Facebook Page" : "Instagram"}
    </span>
  </div>
</div>
```

---

## Step 6: Test It Manually

1. Start backend and frontend:
   ```powershell
   # Terminal 1 (Backend)
   cd C:\Mycodes\Meerkat\meerkat-backend
   .\venv\Scripts\uvicorn main:app --reload --port 8000
   
   # Terminal 2 (Frontend)
   cd C:\Mycodes\Meerkat\meerkat-frontend
   npm run dev
   ```
2. Send a test message from a real Facebook user account to your subscribed test Page.
3. Observe the backend webhook logs:
   - Check that Meta Graph API profile lookup returns the user's name (e.g. `Maria Santos`).
4. Refresh/open Dashboard:
   - Confirm the sidebar and chat header display **Maria Santos** instead of `User #235048`.

---

## Step 7: Write Automated Tests

In `meerkat-backend/test_main.py`:
- Add test verifying that `GET /api/messages` returns `sender_name` and `sender_profile_pic`.
- Test webhook ingestion saving the customer display name.

---

## ✅ Implementation Checklist

- [ ] Add `sender_name` and `sender_profile_pic` columns to `models.Message` in `models.py`
- [ ] Implement `fetch_customer_profile` helper using `httpx`
- [ ] Connect profile lookup in `routes/webhooks.py` with DB caching to avoid redundant API calls
- [ ] Include `sender_name` and `sender_profile_pic` in `routes/messages.py` API response
- [ ] Update `DashboardView.jsx` to render real customer names and avatars with fallback to PSID
- [ ] Run backend tests (`pytest`) and linters (`ruff`)
- [ ] Run frontend tests (`vitest`) and linters (`eslint`)
