import hashlib
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy.orm import Session

import database
import models

# ======== ROUTER INITIALIZATION =======
# create a router for webhook receiving links
router = APIRouter(prefix="/api/webhook", tags=["webhook"])

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
    db: Session = Depends(database.get_db)
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
            hashlib.sha256
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
                    # create new message record
                    msg = models.Message(
                        platform="facebook",
                        sender_id=sender.get("id", ""),
                        recipient_id=recipient.get("id", ""),
                        message_text=message_obj.get("text", "")
                    )
                    # add message to database session
                    db.add(msg)

            # check for instagram dm changes events
            for change in entry.get("changes", []):
                # check if field is value with message details
                value = change.get("value", {})
                # check if message text exists in change value
                if "message" in value:
                    # create new instagram message record
                    msg = models.Message(
                        platform="instagram",
                        sender_id=value.get("from", {}).get("id", ""),
                        recipient_id=value.get("to", {}).get("id", ""),
                        message_text=value.get("message", "")
                    )
                    # add message to database session
                    db.add(msg)

        # save all ingested messages permanently in database
        db.commit()

    # send success status reply back to meta
    return {"status": "ok"}
