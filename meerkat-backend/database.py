import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ======== LOAD ENV =======
# get the hidden variables from the env file
load_dotenv()

# ======== DATABASE CONFIGURATION =======
# get the database link or use a local test file if not found
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# change postgres to postgresql so the tool can read it
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# set up extra settings if we are using the local test file
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# ======== DATABASE ENGINE =======
# build the main connection to the database
engine = create_engine(DATABASE_URL, connect_args=connect_args)
# create a factory that makes database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# make a base class for our database tables
Base = declarative_base()

# ======== DATABASE DEPENDENCY =======
# provide a database connection when needed
def get_db():
    # open a new connection
    db = SessionLocal()
    try:
        # give the connection to the code that asked for it
        yield db
    finally:
        # close the connection when done
        db.close()
