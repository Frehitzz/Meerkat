import hashlib
import hmac
import os

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy.orm import Session

import database
import models
import security

# ======== ROUTER INITIALIZATION =======
# create a router for webhook receiving links
router = APIRouter(prefix="/api/webhook", tags=["webhook"])

# ======== FETCH CUSTOMER PROFILE =======
# get customer name and profile image from meta graph api
async def fetch_customer_profile(sender_psid: str, recipient_page_id: str, access_token: str) -> dict:
    # return empty if missing sender id or token
    if not sender_psid or not access_token:
        return {}

    try:
        # open async http client with timeout
        async with httpx.AsyncClient(timeout=5.0) as client:
            # resolve page access token directly from page id endpoint
            token_to_use = access_token
            if recipient_page_id:
                page_url = f"https://graph.facebook.com/v19.0/{recipient_page_id}"
                page_res = await client.get(
                    page_url,
                    params={"fields": "access_token", "access_token": access_token},
                )
                if page_res.status_code == 200:
                    token_to_use = page_res.json().get("access_token") or access_token

            # fallback to me/accounts if page endpoint did not provide token
            if token_to_use == access_token:
                accounts_url = "https://graph.facebook.com/v19.0/me/accounts"
                acc_res = await client.get(accounts_url, params={"access_token": access_token})
                if acc_res.status_code == 200:
                    pages_data = acc_res.json().get("data", [])
                    for page in pages_data:
                        if str(page.get("id")) == str(recipient_page_id):
                            token_to_use = page.get("access_token") or access_token
                            break
                    if token_to_use == access_token and pages_data:
                        token_to_use = pages_data[0].get("access_token") or access_token

            # build graph api user profile request url using page token
            url = f"https://graph.facebook.com/v19.0/{sender_psid}"
            params = {
                "fields": "first_name,last_name,name,profile_pic",
                "access_token": token_to_use,
            }

            # send get request to graph api
            response = await client.get(url, params=params)
            # check if request succeeded
            if response.status_code == 200:
                data = response.json()
                first_name = data.get("first_name", "")
                last_name = data.get("last_name", "")
                full_name = data.get("name") or f"{first_name} {last_name}".strip()
                # return customer profile dict
                return {
                    "name": full_name or None,
                    "profile_pic": data.get("profile_pic"),
                }
    except (httpx.HTTPError, KeyError, ValueError):
        # return empty dict if network or request fails
        return {}

    return {}




# ======== WEBHOOK VERIFICATION =======
# link meta calls to verify server setup
@router.get("")
def verify_webhook(request: Request):
    # get query parameters sent by meta
    params = request.query_params
    # get mode parameter
    mode = params.get("hub.mode")
    # get verify token parameter
    token = params.get("hub.verify_token")
    # get challenge parameter
    challenge = params.get("hub.challenge")

    # get expected verify token from environment
    expected_token = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "")

    # check if mode is subscribe and token matches
    if mode == "subscribe" and token == expected_token:
        # return challenge number back as plain text to complete handshake
        return Response(content=challenge, media_type="text/plain")
    else:
        # raise error if token does not match
        raise HTTPException(status_code=403, detail="Webhook verification failed")

# ======== WEBHOOK MESSAGE RECEIVER =======
# link meta calls when new message arrives
@router.post("")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(database.get_db),
):
    # read raw body bytes from request
    body_bytes = await request.body()
    # get meta app secret from environment
    app_secret = os.getenv("META_APP_SECRET", "")

    # verify request signature if app secret is configured and signature header present
    if app_secret and x_hub_signature_256 and x_hub_signature_256.startswith("sha256="):
        # extract signature hex string
        expected_sig = x_hub_signature_256.split("sha256=")[1]
        # generate sha256 hmac signature from body bytes using app secret
        generated_sig = hmac.new(
            app_secret.encode(),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        # check if generated signature matches signature sent by meta
        if not hmac.compare_digest(generated_sig, expected_sig):
            # raise error if signatures do not match
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    # parse body bytes into json object
    payload = await request.json()

    # check if payload contains entry list
    if "entry" in payload:
        # loop through all entries in payload
        for entry in payload.get("entry", []):
            # check for page messenger events
            for messaging_event in entry.get("messaging", []):
                # get sender object
                sender = messaging_event.get("sender", {})
                # get recipient object
                recipient = messaging_event.get("recipient", {})
                # get message details object
                message_obj = messaging_event.get("message", {})

                # check if message text exists
                if "text" in message_obj:
                    sender_psid = sender.get("id", "")
                    recipient_page_id = recipient.get("id", "")

                    # check if customer name already exists in database
                    cached_msg = (
                        db.query(models.Message)
                        .filter(
                            models.Message.sender_id == sender_psid,
                            models.Message.sender_name.isnot(None),
                        )
                        .first()
                    )

                    sender_name = cached_msg.sender_name if cached_msg else None
                    sender_pic = cached_msg.sender_profile_pic if cached_msg else None

                    # if customer profile not cached, attempt meta graph api lookup
                    if not sender_name:
                        seller = db.query(models.Seller).first()
                        if seller and seller.encrypted_access_token:
                            token = security.decrypt_token(seller.encrypted_access_token)
                            profile = await fetch_customer_profile(sender_psid, recipient_page_id, token)
                            sender_name = profile.get("name")
                            sender_pic = profile.get("profile_pic")


                    # create new message record with resolved sender details
                    msg = models.Message(
                        platform="facebook",
                        sender_id=sender_psid,
                        sender_name=sender_name,
                        sender_profile_pic=sender_pic,
                        recipient_id=recipient_page_id,
                        message_text=message_obj.get("text", ""),
                    )
                    # add message to database session
                    db.add(msg)

            # check for instagram dm changes events
            for change in entry.get("changes", []):
                # check if field is value with message details
                value = change.get("value", {})
                # check if message text exists in change value
                if "message" in value:
                    from_user = value.get("from", {})
                    ig_username = from_user.get("username") or from_user.get("name")
                    # create new instagram message record
                    msg = models.Message(
                        platform="instagram",
                        sender_id=from_user.get("id", ""),
                        sender_name=ig_username,
                        recipient_id=value.get("to", {}).get("id", ""),
                        message_text=value.get("message", ""),
                    )
                    # add message to database session
                    db.add(msg)

        # save all ingested messages permanently in database
        db.commit()

    # send success status reply back to meta
    return {"status": "ok"}

