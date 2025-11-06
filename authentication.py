from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from functools import wraps
import logging
from jose import jwt
from datetime import datetime, timedelta, timezone


# Configuration
SECRET_KEY = "5ef8bb3634321cc91db8fa5f037e7b83" 
ALGORITHM = "HS256"
TOKEN_EXPIRY = 60 


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

pwd_context = CryptContext(schemes = ["bcrypt"],deprecated="auto")


def hash_pwd(password: str):
    return pwd_context.hash(password)

def verify_password(plain_pwd, hash_pwd):
    return pwd_context.verify(plain_pwd, hash_pwd)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "/login")



