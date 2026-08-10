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
