from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import database
import models
import security

# ======== BEARER SCHEME SETUP =======
# set up http bearer token extractor
bearer_scheme = HTTPBearer(auto_error=False)

# ======== GET CURRENT SELLER =======
# dependency that gets authenticated seller from bearer token
def get_current_seller(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(database.get_db),
) -> models.Seller:
    # check if authorization header is missing
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # decode seller id from jwt token
    seller_id = security.decode_access_token(credentials.credentials)
    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # find seller in database
    seller = db.query(models.Seller).filter_by(id=seller_id).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # return authenticated seller object
    return seller
