from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from typing import List

from configurations import response_collection, form_collection


def save_response(form_id: str, data: dict):
    """
    Saves a form response and returns a normalized submission dict.
    """

    if not ObjectId.is_valid(form_id):
        raise HTTPException(status_code=400, detail="Invalid form ID format")

    form_object_id = ObjectId(form_id)
    form = form_collection.find_one({"_id": form_object_id})

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if form.get("status") != "published":
        raise HTTPException(status_code=400, detail="Form is not accepting responses")

    response_doc = {
        "form_id": form_object_id,
        "answers": data.get("answers"),
        "submitted_by": data.get("submitted_by"),
        "submitted_at": datetime.utcnow(),
    }

    result = response_collection.insert_one(response_doc)

    response_doc["_id"] = str(result.inserted_id)
    response_doc["form_id"] = str(form_object_id)

    return response_doc



def get_responses_by_form_id(form_id: str) -> List[dict]:
    """
    Fetch all responses for a specific form from MongoDB
    Used for exporting to Google Sheets
    """
    try:
        # Convert form_id string to ObjectId if needed
        if ObjectId.is_valid(form_id):
            form_object_id = ObjectId(form_id)
            query = {"form_id": form_object_id}
        else:
            # If form_id is not ObjectId format, search as string
            query = {"form_id": form_id}
        
        # Fetch all responses for this form
        responses = list(response_collection.find(query))
        
        # Convert ObjectId to string for JSON serialization
        for response in responses:
            response['_id'] = str(response['_id'])
            if isinstance(response.get('form_id'), ObjectId):
                response['form_id'] = str(response['form_id'])
            # Rename submitted_at to created_at for consistency
            if 'submitted_at' in response:
                response['created_at'] = response['submitted_at']
        
        print(f"Found {len(responses)} responses for form {form_id}")
        return responses
        
    except Exception as e:
        print(f"Error fetching responses: {e}")
        return []


def get_responses_since(form_id: str, since_datetime: datetime) -> List[dict]:
    """
    Fetch responses added after a specific timestamp
    Used for incremental syncing to Google Sheets
    """
    try:
        # Convert form_id to ObjectId if needed
        if ObjectId.is_valid(form_id):
            form_object_id = ObjectId(form_id)
            query = {
                "form_id": form_object_id,
                "submitted_at": {"$gte": since_datetime}
            }
        else:
            query = {
                "form_id": form_id,
                "submitted_at": {"$gte": since_datetime}
            }
        
        # Fetch responses created after the timestamp
        responses = list(response_collection.find(query))
        
        # Convert ObjectId to string
        for response in responses:
            response['_id'] = str(response['_id'])
            if isinstance(response.get('form_id'), ObjectId):
                response['form_id'] = str(response['form_id'])
            # Rename submitted_at to created_at for consistency
            if 'submitted_at' in response:
                response['created_at'] = response['submitted_at']
        
        print(f"Found {len(responses)} new responses since {since_datetime}")
        return responses
        
    except Exception as e:
        print(f"Error fetching responses since timestamp: {e}")
        return []
