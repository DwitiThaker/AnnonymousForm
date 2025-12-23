from typing import List, Optional
from datetime import datetime
from bson import ObjectId

# Import your MongoDB collection
from configurations import get_access_code_batch_collection


def save_access_code_batch(batch_data: dict) -> str:
    """
    Save access code batch to MongoDB
    Returns the batch_id as string
    """
    try:
        collection = get_access_code_batch_collection()
        result = collection.insert_one(batch_data)
        batch_id = str(result.inserted_id)
        print(f"Access code batch saved with ID: {batch_id}")
        return batch_id
    except Exception as e:
        print(f"Error saving access code batch: {e}")
        raise


def get_access_code_batch(batch_id: str) -> Optional[dict]:
    """Get a specific batch by ID"""
    try:
        collection = get_access_code_batch_collection()
        batch = collection.find_one({"_id": ObjectId(batch_id)})
        if batch:
            batch['_id'] = str(batch['_id'])
        return batch
    except Exception as e:
        print(f"Error fetching batch: {e}")
        return None


def get_all_batches(form_id: Optional[str] = None) -> List[dict]:
    """Get all batches, optionally filtered by form_id"""
    try:
        collection = get_access_code_batch_collection()
        
        query = {}
        if form_id:
            query['form_id'] = form_id
        
        batches = list(collection.find(query).sort("created_at", -1))
        
        # Convert ObjectId to string
        for batch in batches:
            batch['_id'] = str(batch['_id'])
        
        return batches
    except Exception as e:
        print(f"Error fetching batches: {e}")
        return []


def validate_access_code(email: str, code: str, form_id: str) -> dict:
    """
    Validate if access code is valid and not exceeded limit
    Returns: {"valid": bool, "message": str, "code_data": dict}
    """
    try:
        collection = get_access_code_batch_collection()
        
        # Find batch with this code
        batch = collection.find_one({
            "form_id": form_id,
            "codes.email": email,
            "codes.code": code
        })
        
        if not batch:
            return {
                "valid": False,
                "message": "Invalid access code or email",
                "code_data": None
            }
        
        # Find the specific code in the batch
        code_data = None
        for access_code in batch['codes']:
            if access_code['email'] == email and access_code['code'] == code:
                code_data = access_code
                break
        
        if not code_data:
            return {
                "valid": False,
                "message": "Code not found",
                "code_data": None
            }
        
        # Check if code is still valid
        if not code_data.get('is_valid', True):
            return {
                "valid": False,
                "message": "Access code has been deactivated",
                "code_data": code_data
            }
        
        # Check if limit exceeded
        if code_data['used_count'] >= code_data['limit']:
            return {
                "valid": False,
                "message": "Access code usage limit exceeded",
                "code_data": code_data
            }
        
        return {
            "valid": True,
            "message": "Access code is valid",
            "code_data": code_data
        }
        
    except Exception as e:
        print(f"Error validating access code: {e}")
        return {
            "valid": False,
            "message": f"Error validating code: {str(e)}",
            "code_data": None
        }


def increment_code_usage(email: str, code: str, form_id: str) -> bool:
    """
    Increment the used_count for an access code
    Returns True if successful
    """
    try:
        collection = get_access_code_batch_collection()
        
        result = collection.update_one(
            {
                "form_id": form_id,
                "codes.email": email,
                "codes.code": code
            },
            {
                "$inc": {"codes.$.used_count": 1}
            }
        )
        
        if result.modified_count > 0:
            print(f"Incremented usage for code {code} ({email})")
            return True
        else:
            print(f"No code found to increment for {email}")
            return False
            
    except Exception as e:
        print(f"Error incrementing code usage: {e}")
        return False