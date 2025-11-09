from datetime import datetime
import string
import random
from fastapi import APIRouter, HTTPException
import logging
from bson import ObjectId

from MongoDB.schemas import AccessCodeBatchCreate, AccessCodeSchema
from MongoDB.models import AccessCode, AccessCodeBatch
from configurations import access_code_batch_collection, form_collection
from Routes.sendCode import send_access_code


logger = logging.getLogger(__name__)
create_access_code_route = APIRouter()


@create_access_code_route.post("/send_code")
def create_access_code(batch_data: AccessCodeBatchCreate):
    try: 
        logger.info(f"create_access_code: Code is getting created.. ")

        if not ObjectId.is_valid(batch_data.form_id):
            raise HTTPException(status_code=400, detail="Invalid form_id format")
        
        form_object_id = ObjectId(batch_data.form_id)
        form = form_collection.find_one({"_id": form_object_id})
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        codes=[]
        for email in batch_data.emails:
            generate_code = ''.join([random.choice(string.ascii_uppercase + string.digits) for n in range(6)])
            access_code = AccessCode(
                email=email,
                code= generate_code,
                limit = 1,
                used_count = 0,
                is_valid  = True,
                generated_at=datetime.utcnow()
            )
            codes.append(access_code.dict())

            try:
                send_access_code(generate_code, email)
                logger.info(f"Access code sent to {email}")
            except Exception as mail_err:
                logger.error(f"Failed to send access code email to {email}: {mail_err}")

        batch_doc = AccessCodeBatch(
            emails=batch_data.emails,
            form_id=batch_data.form_id,
            generated_by=batch_data.generated_by,
            created_at=datetime.utcnow(),
            codes=[AccessCode(**c) for c in codes]
        )

        result = access_code_batch_collection.insert_one(batch_doc.dict())
        return {"message": "Access codes created successfully", "batch_id": str(result.inserted_id)}
            
    except Exception as e:
        logger.error(f"create_access_code: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while generating access codes.")


