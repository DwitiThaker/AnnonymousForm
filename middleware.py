from fastapi import HTTPException, FastAPI, Request, Depends
from typing import Annotated
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import logging

from authentication import *
from Services.adminServices import get_user_by_email

logger = logging.getLogger(__name__)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role : str = payload.get("role")
        email: str = payload.get("email")
        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except ExpiredSignatureError as Ee:
        logger.error(f"get_current_user: ....{Ee}")
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError as Ie:
        logger.error(f"get_current_user: Invalid token - {Ie}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print("Unexpected error in get_current_user:", str(e))
        logger.error(f"get_current_user: Unexpected error - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")



def admin_required(user = Depends(get_current_user)):
    try:
        print(f"admin_required called with user: {user.get('email', 'Unknown')}")  
        if user.get("role") != "admin":
            print(f"Access denied: User role is {user.get('role')}")  
            raise HTTPException(status_code=403, detail="Admin access required")
        return user
    except Exception as e:
        print("Admin check failed:", str(e))
        raise

