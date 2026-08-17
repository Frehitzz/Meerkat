import os
from datetime import datetime, timedelta, timezone

import jwt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# ======== LOAD ENV =======
# read hidden variables from environment
load_dotenv()

# ======== ENCRYPTION SETUP =======
# get secret key from hidden environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
# get jwt secret key from hidden environment
JWT_SECRET = os.getenv("JWT_SECRET", "meerkat_dev_jwt_secret_key_12345")
# get jwt hashing algorithm
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
# get jwt expiration hours
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "168"))

# check if key exists
if ENCRYPTION_KEY:
    # build encryption tool using key
    fernet = Fernet(ENCRYPTION_KEY.encode())
else:
    # create temporary key if running in test environment
    _fallback_key = Fernet.generate_key()
    # build encryption tool using fallback key
    fernet = Fernet(_fallback_key)

# ======== ENCRYPT TOKEN =======
# function to lock secret token safely
def encrypt_token(token: str) -> str:
    # change text token into encrypted bytes and return string
    return fernet.encrypt(token.encode()).decode()

# ======== DECRYPT TOKEN =======
# function to unlock secret token
def decrypt_token(encrypted_token: str) -> str:
    # decrypt text token using key and return clean string
    return fernet.decrypt(encrypted_token.encode()).decode()

# ======== CREATE JWT SESSION TOKEN =======
# create signed jwt session token for seller
def create_access_token(seller_id: int) -> str:
    # calculate expiration time
    expire_time = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    # build payload dictionary
    payload = {
        "sub": str(seller_id),
        "exp": expire_time,
        "iat": datetime.now(timezone.utc),
    }
    # sign token with jwt secret and algorithm
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ======== VERIFY JWT SESSION TOKEN =======
# verify and decode seller id from jwt token
def decode_access_token(token: str) -> int | None:
    try:
        # decode and verify token signature
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # return seller id integer
        return int(payload.get("sub"))
    except (jwt.PyJWTError, ValueError, TypeError):
        # return none if token is invalid or expired
        return None

