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
