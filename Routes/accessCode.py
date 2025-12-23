# # from datetime import datetime
# # import string
# # import random
# # from fastapi import APIRouter, HTTPException
# # import logging
# # from bson import ObjectId

# # from MongoDB.schemas import AccessCodeBatchCreate, AccessCodeSchema
# # from MongoDB.models import AccessCode, AccessCodeBatch
# # from configurations import access_code_batch_collection, form_collection
# # from Routes.sendCode import send_access_code


# # logger = logging.getLogger(__name__)
# # create_access_code_route = APIRouter()


# # @create_access_code_route.post("/send_code")
# # def create_access_code(batch_data: AccessCodeBatchCreate):
# #     try: 
# #         logger.info(f"create_access_code: Code is getting created.. ")

# #         if not ObjectId.is_valid(batch_data.form_id):
# #             raise HTTPException(status_code=400, detail="Invalid form_id format")
        
# #         form_object_id = ObjectId(batch_data.form_id)
# #         form = form_collection.find_one({"_id": form_object_id})
# #         if not form:
# #             raise HTTPException(status_code=404, detail="Form not found")

# #         codes=[]
# #         for email in batch_data.emails:
# #             generate_code = ''.join([random.choice(string.ascii_uppercase + string.digits) for n in range(6)])
# #             access_code = AccessCode(
# #                 email=email,
# #                 code= generate_code,
# #                 limit = 1,
# #                 used_count = 0,
# #                 is_valid  = True,
# #                 generated_at=datetime.utcnow()
# #             )
# #             codes.append(access_code.dict())

# #             try:
# #                 send_access_code(generate_code, email)
# #                 logger.info(f"Access code sent to {email}")
# #             except Exception as mail_err:
# #                 logger.error(f"Failed to send access code email to {email}: {mail_err}")

# #         batch_doc = AccessCodeBatch(
# #             emails=batch_data.emails,
# #             form_id=batch_data.form_id,
# #             generated_by=batch_data.generated_by,
# #             created_at=datetime.utcnow(),
# #             codes=[AccessCode(**c) for c in codes]
# #         )

# #         result = access_code_batch_collection.insert_one(batch_doc.dict())
# #         return {
# #     "message": "Access codes created successfully",
# #     "batch_id": str(result.inserted_id),
# #     "codes": [{"email": c["email"], "code": c["code"]} for c in codes]
# # }

            
# #     except Exception as e:
# #         logger.error(f"create_access_code: {e}")
# #         raise HTTPException(status_code=500, detail="An unexpected error occurred while generating access codes.")



# from datetime import datetime
# import string
# import random
# from fastapi import APIRouter, HTTPException
# import logging
# from bson import ObjectId

# from MongoDB.schemas import AccessCodeBatchCreate
# from MongoDB.models import AccessCode, AccessCodeBatch
# from configurations import (
#     access_code_batch_collection,
#     form_collection,
#     admin_collection
# )
# from Routes.sendCode import send_access_code


# logger = logging.getLogger(__name__)
# create_access_code_route = APIRouter()



# @create_access_code_route.post("/send_code")
# def send_mail(form_id: str, current_admin: Dict[str, Any] = Depends(admin_required)):
#     try:
#         logger.info("create_access_code: request received")
#     except HTTPException:
#         raise
#     except Exception:
#         logger.exception("create_access_code failed")
#         raise HTTPException(
#             status_code=500,
#             detail="Unexpected error while generating access codes"
#         )


# # @create_access_code_route.post("/send_code")
# # def create_access_code(batch_data: AccessCodeBatchCreate):
# #     try:
# #         print("hello")
# #         logger.info("create_access_code: request received")
# #         logger.info(f"generated_by received: {batch_data.generated_by}")


# #         # 1️⃣ Validate form
# #         if not ObjectId.is_valid(batch_data.form_id):
# #             raise HTTPException(status_code=400, detail="Invalid form_id")

# #         form = form_collection.find_one({"_id": ObjectId(batch_data.form_id)})
# #         if not form:
# #             raise HTTPException(status_code=404, detail="Form not found")

# #         # 2️⃣ Validate admin
# #         admin = admin_collection.find_one({"email": batch_data.generated_by})
# #         if not admin:
# #             raise HTTPException(status_code=403, detail="Admin not authorized")

# #         if not admin.get("is_active", True):
# #             raise HTTPException(status_code=403, detail="Admin account disabled")

# #         # 3️⃣ Validate SMTP config
# #         required_fields = [
# #             "smtp_server",
# #             "smtp_port",
# #             "smtp_username",
# #             "smtp_password",
# #             "smtp_from"
# #         ]
# #         for field in required_fields:
# #             if field not in admin:
# #                 raise HTTPException(
# #                     status_code=500,
# #                     detail=f"Admin SMTP config incomplete: missing {field}"
# #                 )

# #         smtp_config = {
# #             "smtp_server": admin["smtp_server"],
# #             "smtp_port": admin["smtp_port"],
# #             "smtp_username": admin["smtp_username"],
# #             "smtp_password": admin["smtp_password"],
# #             "smtp_from": admin["smtp_from"],
# #             "use_tls": admin.get("smtp_use_tls", True),
# #         }

# #         codes = []
# #         successful_emails = []

# #         # 4️⃣ Generate & send codes
# #         for email in batch_data.emails:
# #             access_code = ''.join(
# #                 random.choices(string.ascii_uppercase + string.digits, k=6)
# #             )

# #             try:
# #                 send_access_code(
# #                     access_code=access_code,
# #                     recipient_email=email,
# #                     **smtp_config
# #                 )

# #                 codes.append(
# #                     AccessCode(
# #                         email=email,
# #                         code=access_code,
# #                         limit=1,
# #                         used_count=0,
# #                         is_valid=True,
# #                         generated_at=datetime.utcnow()
# #                     ).dict()
# #                 )
# #                 successful_emails.append(email)

# #                 logger.info(f"Code sent to {email}")

# #             except Exception as e:
# #                 logger.error(f"Failed to send code to {email}: {e}")

# #         if not codes:
# #             raise HTTPException(
# #                 status_code=500,
# #                 detail="Failed to send access codes to all recipients"
# #             )

# #         # 5️⃣ Save batch
# #         batch_doc = AccessCodeBatch(
# #             emails=successful_emails,
# #             form_id=batch_data.form_id,
# #             generated_by=batch_data.generated_by,
# #             created_at=datetime.utcnow(),
# #             codes=codes
# #         )

# #         result = access_code_batch_collection.insert_one(batch_doc.dict())

# #         return {
# #             "message": "Access codes created and sent successfully",
# #             "batch_id": str(result.inserted_id),
# #             "sent_count": len(codes)
# #         }

# #     except HTTPException:
# #         raise
# #     except Exception:
# #         logger.exception("create_access_code failed")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Unexpected error while generating access codes"
# #         )
