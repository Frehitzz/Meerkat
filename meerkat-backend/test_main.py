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
