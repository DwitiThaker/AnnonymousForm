from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from bson import ObjectId
from typing import Dict, Any

from configurations import (
    get_selectable_users_collection,
    get_form_collection
)
from MongoDB.schemas import SendToSelectedUsersRequest
from Services.emailServices import generate_access_code, send_bulk_emails_task
from Services.accessCodeService import save_access_code_batch
from MongoDB.models import AccessCode, AccessCodeBatch
from middleware import admin_required
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Send Forms"])


@router.post("/send_to_selected_users")
def send_form_to_selected_users(
    request: SendToSelectedUsersRequest,
    background_tasks: BackgroundTasks,
    current_admin: Dict[str, Any] = Depends(admin_required)
):
    selectable_users = get_selectable_users_collection()
    form_collection = get_form_collection()

    # validate form
    if not ObjectId.is_valid(request.form_id):
        raise HTTPException(status_code=400, detail="Invalid form_id")

    form = form_collection.find_one({"_id": ObjectId(request.form_id)})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if form.get("status") != "published":
        raise HTTPException(status_code=400, detail="Form not published")

    # fetch users
    users = list(selectable_users.find({
        "_id": {"$in": [ObjectId(uid) for uid in request.user_ids]},
        "is_active": True
    }))

    if not users:
        raise HTTPException(status_code=400, detail="No valid users selected")

    emails = [u["email"] for u in users]

    # === REUSE EXISTING LOGIC ===
    email_code_pairs = []
    access_codes = []

    for email in emails:
        code = generate_access_code()
        email_code_pairs.append({"email": email, "code": code})

        access_codes.append(AccessCode(
            email=email,
            code=code,
            limit=request.code_limit,
            used_count=0,
            is_valid=True,
            generated_at=datetime.utcnow()
        ).dict())

    batch = AccessCodeBatch(
        emails=emails,
        form_id=request.form_id,
        generated_by=current_admin["email"],
        form_link=request.form_link,
        created_at=datetime.utcnow(),
        codes=access_codes
    )

    batch_id = save_access_code_batch(batch.dict())

    background_tasks.add_task(
        send_bulk_emails_task,
        email_code_pairs,
        request.form_link
    )

    return {
        "success": True,
        "message": f"Form sent to {len(emails)} users",
        "total_users": len(emails),
        "batch_id": batch_id
    }
