import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
import main
import models

# ======== TEST DATABASE SETUP =======
# set up a temporary in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

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
        encrypted_access_token=encrypted,
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

# test facebook callback error redirect
def test_facebook_callback_error():
    # test callback with error parameter
    response = client.get("/api/auth/facebook/callback?error=access_denied", follow_redirects=False)
    # verify status code is 307 redirect
    assert response.status_code == 307
    # verify redirect location points to frontend with error query parameter
    assert "error=auth_failed" in response.headers["location"]

# test webhook verification handshake endpoint
def test_webhook_verification():
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
                        "message": {"text": "Hello Meerkat!"},
                    }
                ],
            }
        ],
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

# test messages list endpoint
def test_get_messages_endpoint():
    # create tables in test database
    models.database.Base.metadata.create_all(bind=engine)
    # open session
    db = TestingSessionLocal()
    db.query(models.Seller).delete()
    seller = models.Seller(
        facebook_user_id="seller_msg_endpoint_test",
        name="Test Seller Msg",
    )
    db.add(seller)
    db.commit()
    db.refresh(seller)

    # insert sample facebook message
    msg_fb = models.Message(
        platform=models.Platform.FACEBOOK,
        sender_id="fb_user_1",
        recipient_id="page_1",
        message_text="Facebook test inquiry",
    )
    # insert sample instagram message
    msg_ig = models.Message(
        platform=models.Platform.INSTAGRAM,
        sender_id="ig_user_1",
        recipient_id="page_1",
        message_text="Instagram test inquiry",
    )
    db.add(msg_fb)
    db.add(msg_ig)
    db.commit()

    import security
    token = security.create_access_token(seller.id)
    headers = {"Authorization": f"Bearer {token}"}
    db.close()

    # get all messages
    res_all = client.get("/api/messages", headers=headers)
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert data_all["status"] == "success"
    assert data_all["count"] >= 2

    # get filtered facebook messages
    res_fb = client.get("/api/messages?platform=facebook", headers=headers)
    assert res_fb.status_code == 200
    data_fb = res_fb.json()
    assert all(m["platform"] == "facebook" for m in data_fb["messages"])

    # get filtered instagram messages
    res_ig = client.get("/api/messages?platform=instagram", headers=headers)
    assert res_ig.status_code == 200
    data_ig = res_ig.json()
    assert all(m["platform"] == "instagram" for m in data_ig["messages"])


# test getting all messages with sorting and field verification
def test_get_all_messages_for_seller():
    # create tables in test database
    models.database.Base.metadata.create_all(bind=engine)
    # open session
    db = TestingSessionLocal()
    # clear existing messages to have a clean count
    db.query(models.Message).delete()
    db.query(models.Seller).delete()
    db.commit()

    # insert sample seller
    seller = models.Seller(
        facebook_user_id="seller_msg_test",
        name="Test Seller",
    )
    db.add(seller)
    db.commit()
    db.refresh(seller)

    # insert sample messages across platforms
    m1 = models.Message(
        platform=models.Platform.FACEBOOK,
        sender_id="fb_user_101",
        recipient_id="page_target",
        message_text="First message from FB",
    )
    m2 = models.Message(
        platform=models.Platform.INSTAGRAM,
        sender_id="ig_user_202",
        recipient_id="page_target",
        message_text="Second message from IG",
    )
    m3 = models.Message(
        platform=models.Platform.FACEBOOK,
        sender_id="fb_user_303",
        recipient_id="page_other",
        message_text="Third message from FB other page",
    )
    # add messages to database
    db.add_all([m1, m2, m3])
    db.commit()

    # generate jwt token for seller
    import security
    token = security.create_access_token(seller.id)
    headers = {"Authorization": f"Bearer {token}"}
    db.close()

    # request all messages from endpoint with bearer auth
    response = client.get("/api/messages", headers=headers)
    # verify response status is 200
    assert response.status_code == 200
    data = response.json()
    # verify response status is success
    assert data["status"] == "success"
    # verify count matches all inserted messages
    assert data["count"] == 3
    assert len(data["messages"]) == 3

    # verify all required fields exist on every message
    for msg in data["messages"]:
        assert "id" in msg
        assert "platform" in msg
        assert "sender_id" in msg
        assert "sender_name" in msg
        assert "sender_profile_pic" in msg
        assert "recipient_id" in msg
        assert "message_text" in msg
        assert "created_at" in msg

    # verify filtering with platform=all returns all messages
    res_all_filter = client.get("/api/messages?platform=all", headers=headers)
    assert res_all_filter.status_code == 200
    assert res_all_filter.json()["count"] == 3

    # verify filtering by specific recipient page
    res_recipient = client.get("/api/messages?recipient_id=page_target", headers=headers)
    assert res_recipient.status_code == 200
    assert res_recipient.json()["count"] == 2

# ======== AUTH & SESSION MIDDLEWARE TESTS =======
# test creating and decoding jwt access token
def test_access_token_creation_and_decoding():
    import security
    token = security.create_access_token(42)
    assert token is not None
    assert isinstance(token, str)
    decoded_id = security.decode_access_token(token)
    assert decoded_id == 42

    # test decoding invalid token returns none
    assert security.decode_access_token("invalid.jwt.token") is None

# test get me endpoint with valid bearer token
def test_get_me_endpoint_with_valid_token():
    models.database.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.query(models.Seller).delete()
    seller = models.Seller(
        facebook_user_id="seller_me_test",
        name="Elena Ramos",
    )
    db.add(seller)
    db.commit()
    db.refresh(seller)

    import security
    token = security.create_access_token(seller.id)
    db.close()

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == seller.id
    assert data["name"] == "Elena Ramos"
    assert data["facebook_user_id"] == "seller_me_test"

# test get me endpoint returns 401 when unauthorized
def test_get_me_endpoint_unauthorized():
    # request without auth header
    response = client.get("/api/auth/me")
    assert response.status_code == 401

    # request with invalid bearer token
    response_invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer fake_token"})
    assert response_invalid.status_code == 401

# test messages endpoint requires auth
def test_get_messages_unauthorized():
    response = client.get("/api/messages")
    assert response.status_code == 401


# test customer profile resolution and caching during webhook ingestion
def test_webhook_customer_profile_resolution(monkeypatch):
    # create tables in test database
    models.database.Base.metadata.create_all(bind=engine)
    # open database session
    db = TestingSessionLocal()
    # clear existing messages and sellers
    db.query(models.Message).delete()
    db.query(models.Seller).delete()
    db.commit()


    # insert sample seller with encrypted access token
    import security
    encrypted_tok = security.encrypt_token("EAAB_test_page_token")
    seller = models.Seller(
        facebook_user_id="seller_fb_123",
        name="Shop Owner",
        encrypted_access_token=encrypted_tok,
    )
    db.add(seller)
    db.commit()
    db.close()

    # mock fetch_customer_profile helper
    from routes import webhooks
    async def mock_fetch_customer_profile(sender_psid, recipient_page_id, access_token):
        return {
            "name": "Maria Santos",
            "profile_pic": "https://example.com/maria.jpg",
        }

    monkeypatch.setattr(webhooks, "fetch_customer_profile", mock_fetch_customer_profile)


    # simulate incoming facebook webhook payload
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "page_456",
                "messaging": [
                    {
                        "sender": {"id": "user_maria_99"},
                        "recipient": {"id": "page_456"},
                        "message": {"text": "Hello, how much is the bag?"},
                    }
                ],
            }
        ],
    }

    # send webhook request
    res = client.post("/api/webhook", json=payload)
    assert res.status_code == 200

    # open session to verify saved message with resolved customer name
    db = TestingSessionLocal()
    saved = db.query(models.Message).filter_by(sender_id="user_maria_99").first()
    assert saved is not None
    assert saved.sender_name == "Maria Santos"
    assert saved.sender_profile_pic == "https://example.com/maria.jpg"
    assert saved.message_text == "Hello, how much is the bag?"
    db.close()


