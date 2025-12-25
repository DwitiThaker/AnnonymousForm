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
    try:
        if ObjectId.is_valid(form_id):
            form_object_id = ObjectId(form_id)
            query = {"form_id": form_object_id}
        else:
            query = {"form_id": form_id}
        
        responses = list(response_collection.find(query))
        
        for response in responses:
            response['_id'] = str(response['_id'])
            if isinstance(response.get('form_id'), ObjectId):
                response['form_id'] = str(response['form_id'])
            if 'submitted_at' in response:
                response['created_at'] = response['submitted_at']
        
        print(f"Found {len(responses)} responses for form {form_id}")
        return responses
        
    except Exception as e:
        print(f"Error fetching responses: {e}")
        return []


def get_responses_since(form_id: str, since_datetime: datetime) -> List[dict]:
    try:
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
        
        responses = list(response_collection.find(query))
        
        for response in responses:
            response['_id'] = str(response['_id'])
            if isinstance(response.get('form_id'), ObjectId):
                response['form_id'] = str(response['form_id'])
            if 'submitted_at' in response:
                response['created_at'] = response['submitted_at']
        
        print(f"Found {len(responses)} new responses since {since_datetime}")
        return responses
        
    except Exception as e:
        print(f"Error fetching responses since timestamp: {e}")
        return []
