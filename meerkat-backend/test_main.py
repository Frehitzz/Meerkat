from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database
import main
import models

# ======== TEST DATABASE SETUP =======
# set up a temporary in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# import staticpool to keep sqlite connection alive
from sqlalchemy.pool import StaticPool

# build the database engine for tests using staticpool
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# create a session maker for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ======== OVERRIDE DEPENDENCY =======
# make a custom database connection provider for tests
def override_get_db():
    # open a new connection
    db = TestingSessionLocal()
    try:
        # give the connection to the test
        yield db
    finally:
        # close the connection when the test is done
        db.close()

# tell fastapi to use our test database instead of the real database
main.app.dependency_overrides[database.get_db] = override_get_db

# ======== TEST CLIENT =======
# create the test client to make API requests
client = TestClient(main.app)

# ======== TESTS =======
# test the root endpoint to make sure it is working
def test_root():
    # create the tables in our test database
    models.database.Base.metadata.create_all(bind=engine)
    # make a get request to the root link
    response = client.get("/")
    # make sure the request worked
    assert response.status_code == 200
    # make sure the reply text is correct
    assert response.json() == {"status": "Meerkat backend running"}

# test the ping endpoint to make sure it is working
def test_ping():
    # make a get request to the ping link
    response = client.get("/api/ping")
    # make sure the request worked
    assert response.status_code == 200
    # make sure the reply text is correct
    assert response.json() == {"message": "pong from FastAPI"}

# test adding and reading items in the database
def test_database_endpoints():
    # create the tables in our test database
    models.database.Base.metadata.create_all(bind=engine)
    # make a post request to add a new test item
    post_response = client.post("/api/test-db?name=TestUser")
    # make sure the request worked
    assert post_response.status_code == 200
    # make sure the reply message is correct
    assert post_response.json()["message"] == "Item created successfully"
    # make sure the item name is correct
    assert post_response.json()["item"]["name"] == "TestUser"

    # make a get request to read all the items
    get_response = client.get("/api/test-db")
    # make sure the request worked
    assert get_response.status_code == 200
    # make sure we get a list of items back
    assert "items" in get_response.json()
    # make sure the list is not empty
    assert len(get_response.json()["items"]) > 0


# test encryption and seller database model
def test_security_and_seller_model():
    import security
    # sample token string
    raw_token = "EAAB1234567890abcdef"
    # encrypt the token
    encrypted = security.encrypt_token(raw_token)
    # verify it is encrypted and not equal to raw token
    assert encrypted != raw_token
    # decrypt the token back
    decrypted = security.decrypt_token(encrypted)
    # verify decrypted token matches original
    assert decrypted == raw_token

    # create tables in test database
    models.database.Base.metadata.create_all(bind=engine)
    # open session
    db = TestingSessionLocal()
    # create new seller
    seller = models.Seller(
        facebook_user_id="123456789",
        name="Test Seller",
        encrypted_access_token=encrypted
    )
    # add seller to session
    db.add(seller)
    # commit seller to database
    db.commit()
    # refresh seller instance
    db.refresh(seller)

    # query seller from database
    fetched = db.query(models.Seller).filter_by(facebook_user_id="123456789").first()
    # verify seller exists
    assert fetched is not None
    # verify seller name matches
    assert fetched.name == "Test Seller"
    # verify decrypted token matches original
    assert security.decrypt_token(fetched.encrypted_access_token) == raw_token
    # close test session
    db.close()


# test facebook oauth redirect endpoint
def test_facebook_login_redirect():
    # make get request to facebook auth endpoint without following redirects
    response = client.get("/api/auth/facebook", follow_redirects=False)
    # verify status code is 307 temporary redirect
    assert response.status_code == 307
    # verify redirect location points to facebook oauth dialog
    assert "https://www.facebook.com/v19.0/dialog/oauth" in response.headers["location"]


# test webhook verification handshake endpoint
def test_webhook_verification():
    import os
    # set test verify token in environment
    os.environ["META_WEBHOOK_VERIFY_TOKEN"] = "test_verify_token"

    # test valid verification handshake
    response = client.get("/api/webhook?hub.mode=subscribe&hub.verify_token=test_verify_token&hub.challenge=123456")
    # verify status code is 200 ok
    assert response.status_code == 200
    # verify response content matches challenge string
    assert response.text == "123456"

    # test invalid verification handshake with wrong token
    bad_response = client.get("/api/webhook?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=123456")
    # verify status code is 403 forbidden
    assert bad_response.status_code == 403


# test webhook message ingestion endpoint
def test_webhook_message_ingestion():
    # create tables in test database
    models.database.Base.metadata.create_all(bind=engine)

    # sample webhook payload for facebook messenger
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "1000112233",
                "messaging": [
                    {
                        "sender": {"id": "user_123"},
                        "recipient": {"id": "page_456"},
                        "message": {"text": "Hello Meerkat!"}
                    }
                ]
            }
        ]
    }

    # send post request to webhook endpoint
    response = client.post("/api/webhook", json=payload)
    # verify status code is 200 ok
    assert response.status_code == 200
    # verify response status is ok
    assert response.json() == {"status": "ok"}

    # open session to verify saved message in database
    db = TestingSessionLocal()
    # query message from database
    msg = db.query(models.Message).filter_by(sender_id="user_123").first()
    # verify message exists
    assert msg is not None
    # verify message text matches
    assert msg.message_text == "Hello Meerkat!"
    # verify platform is facebook
    assert msg.platform == "facebook"
    # close session
    db.close()
