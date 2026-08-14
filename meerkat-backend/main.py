from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import database
import models
from routes import auth, messages, webhooks

# ======== DATABASE SETUP =======
# build the database tables if they are not there yet
models.database.Base.metadata.create_all(bind=database.engine)

# ======== APP INITIALIZATION =======
# start the main web app
app = FastAPI()

# allow the web app to talk to the frontend safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://meerkat-app.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== INCLUDE ROUTERS =======
# connect auth router links to main app
app.include_router(auth.router)
# connect webhooks router links to main app
app.include_router(webhooks.router)
# connect messages router links to main app
app.include_router(messages.router)

# ======== ROUTES =======
# set up the main home page link
@app.get("/")
def root():
    # send back a message that the server is working
    return {"status": "Meerkat backend running"}

# set up a simple link to check if server is awake
@app.get("/api/ping")
def ping():
    # send back a simple reply
    return {"message": "pong from FastAPI"}

# set up a link to add new test items
@app.post("/api/test-db")
def create_test_item(name: str, db: Session = Depends(database.get_db)):
    # build the new item using the name given
    new_item = models.TestItem(name=name)
    # tell the database about the new item
    db.add(new_item)
    # save the item permanently in the database
    db.commit()
    # update our item info from the database
    db.refresh(new_item)
    # send back a success message and the new item
    return {"message": "Item created successfully", "item": new_item}

# set up a link to read all test items
@app.get("/api/test-db")
def read_test_items(db: Session = Depends(database.get_db)):
    # ask the database for all the test items
    items = db.query(models.TestItem).all()
    # send the list of items back
    return {"items": items}