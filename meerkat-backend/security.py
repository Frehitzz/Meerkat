import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# ======== LOAD ENV =======
# read hidden variables from environment
load_dotenv()

# ======== ENCRYPTION SETUP =======
# get secret key from hidden environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# check if key exists
if ENCRYPTION_KEY:
    # build encryption tool using key
    fernet = Fernet(ENCRYPTION_KEY.encode())
else:
    # raise error if key is missing
    raise ValueError("ENCRYPTION_KEY missing in env file")

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
