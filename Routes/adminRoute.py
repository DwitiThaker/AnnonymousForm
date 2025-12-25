from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Annotated, Any, Dict
from datetime import datetime


from authentication import *
from Services.adminServices import get_user_by_email, create_user
from MongoDB.schemas import Login, UserOut, UserCreate
from MongoDB.models import Admin  
from middleware import admin_required

admin_auth_route = APIRouter()


@admin_auth_route.post("/login")
def login(login_data: Login):
    db_user = get_user_by_email(login_data.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(login_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token_data = {
        "email": db_user["email"],
        "user_id": str(db_user["_id"]),
        "role": db_user["role"]
    }

    access_token = create_access_token(token_data)

    return {
        "user": UserOut(
            name=db_user["name"],
            email=db_user["email"],
            role=db_user["role"]
        ),
        "access_token": access_token,
        "token_type": "bearer"
    }

    



@admin_auth_route.post("/register", response_model=UserOut)
def register(user: UserCreate):
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = hash_pwd(user.password)
    
    
    new_user = Admin(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role=user.role,
        is_active=True,
        created_at=datetime.utcnow()
    )

    created_user = create_user(new_user) 

    return UserOut(
        name=created_user["name"],
        email=created_user["email"],
        role=created_user["role"],
        is_active=created_user["is_active"]
    )

