from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import database
import models

# ======== ROUTER INITIALIZATION =======
# create a router for messaging and inbox endpoints
router = APIRouter(prefix="/api/messages", tags=["messages"])

# ======== GET MESSAGES LIST =======
# fetch list of customer messages for seller with optional platform filter
@router.get("")
def get_messages(
    platform: str | None = None,
    seller_id: int | None = None,
    recipient_id: str | None = None,
    db: Session = Depends(database.get_db),
):
    # create base query on messages table
    query = db.query(models.Message)

    # filter by platform if provided and not equal to all
    if platform and platform != "all":
        # apply platform filter
        query = query.filter(models.Message.platform == platform)

    # filter by specific recipient page or account id if provided
    if recipient_id:
        # apply recipient filter
        query = query.filter(models.Message.recipient_id == recipient_id)

    # order messages newest first
    messages = query.order_by(models.Message.created_at.desc()).all()

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

