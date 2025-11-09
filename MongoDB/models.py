from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class Form(BaseModel):
    title: str
    description: str
    question: str
    qid: str
    que_type: str
    required: bool
    answer: str
    created_at: datetime
    created_by: str
    status: str

class Response(BaseModel):
    form_id : str
    access_code: str
    submitted_at: datetime
    q_id: int
    answer: str

class Admin(BaseModel):  
    name: str
    email: EmailStr
    password: str
    role: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    access_code: str
    has_submited: str
    submitted_at: datetime

class AccessCode(BaseModel):
    email: EmailStr
    code: str
    limit: int = 1          # number of times this code can be used (e.g. 1 submission)
    used_count: int = 0     # to track how many times it’s been used
    is_valid: bool = True
    generated_at: datetime = datetime.utcnow()

class AccessCodeBatch(BaseModel):
    emails: List[EmailStr]        # array of all emails uploaded
    form_id: str# optional: link to a specific form
    generated_by: str             # admin email or id
    form_link: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    codes: Optional[List[AccessCode]] = []  # generated codes for each email



    



