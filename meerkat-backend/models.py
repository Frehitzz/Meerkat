from sqlalchemy import Column, DateTime, Integer, String
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
