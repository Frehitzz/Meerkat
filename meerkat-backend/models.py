import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

import database


# ======== TEST ITEM MODEL =======
# create the blueprint for the test items table
class TestItem(database.Base):
    # set the name of the table in the database
    __tablename__ = "test_items"

    # make a unique id number for each item
    id = Column(Integer, primary_key=True, index=True)
    # make a text box for the item name
    name = Column(String, index=True)
    # save the exact date and time the item was made
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ======== SELLER MODEL =======
# create the blueprint for the sellers table
class Seller(database.Base):
    # set the name of the table in the database
    __tablename__ = "sellers"

    # make a unique id number for each seller
    id = Column(Integer, primary_key=True, index=True)
    # store the facebook user id
    facebook_user_id = Column(String, unique=True, index=True)
    # store the seller name
    name = Column(String)
    # store the encrypted access token
    encrypted_access_token = Column(String)
    # save the exact date and time the seller signed up
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ======== PLATFORM ENUM =======
# list the allowed platforms for messages
class Platform(str, enum.Enum):
    # platform for facebook messages
    FACEBOOK = "facebook"
    # platform for instagram messages
    INSTAGRAM = "instagram"


# ======== MESSAGE MODEL =======
# create the blueprint for incoming social messages
class Message(database.Base):
    # set the name of the table in the database
    __tablename__ = "messages"

    # make a unique id number for each message
    id = Column(Integer, primary_key=True, index=True)
    # store platform type using our enum
    platform = Column(Enum(Platform), index=True)
    # store sender id from meta
    sender_id = Column(String, index=True)
    # store customer real display name
    sender_name = Column(String, nullable=True)
    # store customer profile picture url
    sender_profile_pic = Column(String, nullable=True)
    # store recipient page or account id
    recipient_id = Column(String, index=True)
    # store message text body
    message_text = Column(String)
    # save date and time message arrived
    created_at = Column(DateTime(timezone=True), server_default=func.now())

