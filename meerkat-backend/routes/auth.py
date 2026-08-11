import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import database
import models
import security

# ======== ROUTER INITIALIZATION =======
# create a router for authentication links
router = APIRouter(prefix="/api/auth", tags=["auth"])

# ======== FACEBOOK LOGIN REDIRECT =======
# link that sends seller to facebook login page
@router.get("/facebook")
def facebook_login():
    # get app id from environment
    app_id = os.getenv("META_APP_ID", "")
    # set the callback link back to our server
    redirect_uri = os.getenv("META_REDIRECT_URI", "http://localhost:8000/api/auth/facebook/callback")
    # use the config_id created in the meta dashboard for business login permissions
    config_id = os.getenv("META_CONFIG_ID", "1535297491677462")
    # build full facebook login url using config_id instead of scope
    fb_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={app_id}&redirect_uri={redirect_uri}&config_id={config_id}&response_type=code"
    )
    # send seller to facebook login
    return RedirectResponse(url=fb_url)

# ======== FACEBOOK LOGIN CALLBACK =======
# link facebook sends code back to after seller approves
@router.get("/facebook/callback")
async def facebook_callback(code: str, db: Session = Depends(database.get_db)):
    # get app id from environment
    app_id = os.getenv("META_APP_ID", "")
    # get app secret from environment
    app_secret = os.getenv("META_APP_SECRET", "")
    # set the callback link used during login
    redirect_uri = os.getenv("META_REDIRECT_URI", "http://localhost:8000/api/auth/facebook/callback")

    # check if code was received
    if not code:
        # raise error if code is missing
        raise HTTPException(status_code=400, detail="Authorization code missing")

    # open http client to talk to facebook graph api
    async with httpx.AsyncClient() as client:
        # exchange code for access token
        token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
        params = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "client_secret": app_secret,
            "code": code,
        }
        # send request to get access token
        response = await client.get(token_url, params=params)
        # check if facebook token request failed
        if response.status_code != 200:
            # raise error with details from facebook
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")
        
        # parse json reply from facebook
        token_data = response.json()
        # get access token string
        access_token = token_data.get("access_token")

        # fetch seller profile details from facebook
        me_url = f"https://graph.facebook.com/v19.0/me?access_token={access_token}"
        # send request to get profile info
        me_response = await client.get(me_url)
        # parse json profile reply
        profile_data = me_response.json()
        
        # get facebook user id
        fb_user_id = profile_data.get("id", "unknown_id")
        # get seller name
        seller_name = profile_data.get("name", "Unknown Seller")

        # ======== SUBSCRIBE PAGES TO WEBHOOKS =======
        # fetch all facebook pages owned by the seller
        accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={access_token}"
        # send request to get pages list
        accounts_response = await client.get(accounts_url)
        # parse json pages reply
        accounts_data = accounts_response.json()

        # loop through all pages the seller owns
        for page in accounts_data.get("data", []):
            # get the unique page id
            page_id = page.get("id")
            # get the specific access token for this page
            page_token = page.get("access_token")
            # prepare the subscription link
            subscribe_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
            # set the fields we want to subscribe to
            subscribe_params = {
                "subscribed_fields": "messages",
                "access_token": page_token
            }
            # send post request to tell meta to forward messages for this page
            await client.post(subscribe_url, data=subscribe_params)

    # encrypt access token safely using security module
    encrypted_token = security.encrypt_token(access_token)

    # find existing seller in database
    seller = db.query(models.Seller).filter_by(facebook_user_id=fb_user_id).first()
    # check if seller exists
    if seller:
        # update seller name
        seller.name = seller_name
        # update seller encrypted access token
        seller.encrypted_access_token = encrypted_token
    else:
        # create new seller record
        seller = models.Seller(
            facebook_user_id=fb_user_id,
            name=seller_name,
            encrypted_access_token=encrypted_token,
        )
        # add seller to database session
        db.add(seller)

    # save changes permanently in database
    db.commit()
    # refresh seller object from database
    db.refresh(seller)

    # return success message with seller details
    return {
        "status": "success",
        "message": "Facebook Login successful",
        "seller": {
            "id": seller.id,
            "facebook_user_id": seller.facebook_user_id,
            "name": seller.name,
        },
    }
