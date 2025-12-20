from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr

class Login(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "admin"

class UserOut(BaseModel):
    name: str
    email: EmailStr
    role: str
    is_active: Optional[bool] = True

class QuestionCreate(BaseModel):
    qid: str
    question_text: str
    que_type: str              
    required: bool
    options: Optional[List[str]] = []  

class FormCreate(BaseModel):
    title: str
    description: Optional[str]
    questions: List[QuestionCreate]    
    created_by: str
    created_at: datetime
    status: str = "active"

class AccessCodeSchema(BaseModel):
    email: EmailStr
    code: str
    limit: int = 1
    used_count: int = 0
    is_valid: bool = True

class AccessCodeBatchCreate(BaseModel):
    emails: List[EmailStr]          
    form_id: Optional[str] = None   
    generated_by: str
    created_at: Optional[datetime] = datetime.utcnow()


class ResponseCreate(BaseModel):
    form_id: str              
    answers: Dict[str, str]   
    submitted_by: str = None  

class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[list] = None

