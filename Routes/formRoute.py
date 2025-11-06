from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Annotated, Any, Dict
from bson import ObjectId
import logging


from authentication import *
from MongoDB.schemas import FormCreate
from configurations import form_collection
from middleware import get_current_user, admin_required

form_route = APIRouter()
logger = logging.getLogger(__name__)


@form_route.post("/create_form")
def create_form(form_data: FormCreate, current_admin: Dict[str, Any] = Depends(admin_required)):

    try: 
        logger.info("create_form: .... ")
        
        # Step 2: Prepare form document for MongoDB
        form_dict = form_data.model_dump()
        form_dict["created_by"] = current_admin["email"]  # use the injected dependency
        form_dict["created_at"] = datetime.utcnow()
        form_dict["status"] = "active"

        # Step 3: Insert into MongoDB
        result = form_collection.insert_one(form_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create form")

        # Step 4: Return success response
        return {
            "message": "Form created successfully",
            "form_id": str(result.inserted_id),
            "created_by": current_admin["email"]
        }
    except Exception as e: 
        logger.error(f"create_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@form_route.get("/get_forms")
def get_forms(current_admin: Dict[str, Any] = Depends(admin_required)):

    # Step 2: Fetch all forms from MongoDB
    forms = list(form_collection.find())

    # Step 3: Convert ObjectId to string
    for form in forms:
        form["_id"] = str(form["_id"])

    # Step 4: Return the list
    return {"total_forms": len(forms), "forms": forms}



@form_route.post("/publish_form")
def publish_form(form_id: str):
    form = form_collection.find_one({"_id": ObjectId(form_id)})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Step 2: Update the form status to 'published'
    update_result = form_collection.update_one(
        {"_id": ObjectId(form_id)},
        {"$set": {"status": "published", "published_at": datetime.utcnow()}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to publish form")
    
    # Step 3: Generate a public link (example: front-end route or API route)
    form_link = f"http://192.168.3.24:8000/forms/public/{form_id}"
    
    return {
        "message": "Form published successfully",
        "form_id": form_id,
        "link": form_link
    }

