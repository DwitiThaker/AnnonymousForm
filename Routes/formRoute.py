from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Any, Dict
from bson import ObjectId
import logging


from authentication import *
from MongoDB.schemas import FormCreate, FormUpdate
from configurations import form_collection, access_code_batch_collection
from middleware import  admin_required

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
    
    # Step 3: Generate a public link (example: front-end route or API route)
    form_link = f"https://annonymousform.onrender.com/forms/public/{form_id}"

    if form.get("status") == "published" and not form.get("form_link"):
        raise HTTPException(
            status_code=500,
            detail="Form is published but missing form_link. Database integrity issue."
        )
    
    update_result = form_collection.update_one(
        {"_id": ObjectId(form_id)},
        {"$set": {"status": "published", "published_at": datetime.utcnow(), "form_link": form_link}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to publish form")
    
    return {
        "message": "Form published successfully",
        "form_id": form_id,
    }



@form_route.post("/unpublish_form")
def unpublish_form(form_id: str, current_admin: Dict[str, Any] = Depends(admin_required)):
    try:
        from bson import ObjectId

        # ✅ Validate BSON ObjectId format
        if not ObjectId.is_valid(form_id):
            raise HTTPException(status_code=400, detail="Invalid form ID")

        form_object_id = ObjectId(form_id)

        # ✅ Check if form exists
        form = form_collection.find_one({"_id": form_object_id})
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        # ✅ If form is already unpublished
        if form.get("status") != "published":
            return {"message": "Form is not published"}

        # ✅ Update form: revert status
        update_result = form_collection.update_one(
            {"_id": form_object_id},
            {
                "$set": {
                    "status": "active",        # back to active/draft mode
                    "updated_at": datetime.utcnow()
                },
                "$unset": {
                    "published_at": "",
                    "form_link": ""
                }
            }
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to unpublish form")

        # ✅ Remove form_link from associated code batches
        access_code_batch_collection.update_many(
            {"form_id": form_object_id},
            {
                "$unset": {"form_link": ""},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        return {
            "message": "Form unpublished successfully",
            "form_id": form_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@form_route.delete("/delete_form/{form_id}")
def delete_form(form_id: str, current_admin: Dict[str, Any] = Depends(admin_required)):

    if not ObjectId.is_valid(form_id):
        raise HTTPException(status_code=400, detail="Invalid form ID")

    result = form_collection.delete_one({"_id": ObjectId(form_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Form not found")

    return {"message": "Form permanently deleted", "form_id": form_id}


@form_route.put("/edit_form/{form_id}")
def edit_form(form_id: str, updated_data: FormUpdate, current_admin: Dict[str, Any] = Depends(admin_required)):
    try:

        # ✅ Validate form ID
        if not ObjectId.is_valid(form_id):
            raise HTTPException(status_code=400, detail="Invalid form ID")

        form_object_id = ObjectId(form_id)

        # ✅ Find the form
        form = form_collection.find_one({"_id": form_object_id})
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        # ✅ Optional (recommended): Block editing published forms
        if form.get("status") == "published":
            raise HTTPException(status_code=400, detail="Cannot edit a published form. Unpublish first.")

        # ✅ Build update document dynamically
        update_fields = {k: v for k, v in updated_data.dict().items() if v is not None}

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        # ✅ Add updated timestamp
        update_fields["updated_at"] = datetime.utcnow()

        # ✅ Perform update
        result = form_collection.update_one(
            {"_id": form_object_id},
            {"$set": update_fields}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update form")

        return {
            "message": "Form updated successfully",
            "form_id": form_id,
            "updated_fields": update_fields
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
