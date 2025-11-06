from MongoDB.models import User, Admin  
from configurations import user_collection
import logging
from pymongo.errors import PyMongoError 
from fastapi import HTTPException


logger = logging.getLogger(__name__)

def create_user(user: Admin):  
    try:
        logger.info(f"create_user: User is getting created.. ")
        user_dict = user.model_dump()
        result = user_collection.insert_one(user_dict)
        user_dict['user_id'] = str(result.inserted_id)
        return user_dict
    except PyMongoError as db_err:
        logger.error(f"create_user: Database error while creating user: {db_err}")
        raise HTTPException(status_code=500, detail="Database insert failed")

def get_user_by_email(email: str):
    try:
        logger.info(f"get_user_by_email: fetching user... ")
        user = user_collection.find_one({"email": email})
        return user
    except PyMongoError as db_err:
        logger.error(f"get_user_by_email: Database error while fetching user '{email}': {db_err}")
        raise HTTPException(status_code=500, detail="Database query failed")