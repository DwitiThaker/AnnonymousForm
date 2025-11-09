from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Any, Dict
from bson import ObjectId
import logging


from authentication import *
from MongoDB.schemas import ResponseCreate
from configurations import response_collection,form_collection


form_route = APIRouter()
logger = logging.getLogger(__name__)

@form_route.post("/submit_response")
def submit_response(response_data: ResponseCreate):
    try:
        from bson import ObjectId

        # ✅ Validate form_id
        if not ObjectId.is_valid(response_data.form_id):
            raise HTTPException(status_code=400, detail="Invalid form ID format")

        form_object_id = ObjectId(response_data.form_id)
        form = form_collection.find_one({"_id": form_object_id})

        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        if form.get("status") != "published":
            raise HTTPException(status_code=400, detail="Form is not live or accepting responses")

        # ✅ Prepare response document
        response_doc = {
            "form_id": form_object_id,
            "answers": response_data.answers,
            "submitted_by": response_data.submitted_by,
            "submitted_at": datetime.utcnow()
        }

        result = response_collection.insert_one(response_doc)

        return {
            "message": "Response submitted successfully",
            "response_id": str(result.inserted_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
