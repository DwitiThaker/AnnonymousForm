from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Any

from configurations import get_selectable_users_collection
from MongoDB.schemas import SelectableUserCreate, SelectableUserOut, DeleteSelectableUsersRequest
from middleware import admin_required

router = APIRouter(prefix="/admin/users", tags=["Selectable Users"])


@router.post("", response_model=SelectableUserOut)
def add_selectable_user(
    user: SelectableUserCreate,
    current_admin: Dict[str, Any] = Depends(admin_required)
):
    collection = get_selectable_users_collection()

    # prevent duplicate emails
    if collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    result = collection.insert_one({
        "name": user.name,
        "email": user.email,
        "is_active": True,
        "created_at": datetime.utcnow()
    })

    return {
        "id": str(result.inserted_id),
        "name": user.name,
        "email": user.email,
        "is_active": True
    }


@router.get("", response_model=List[SelectableUserOut])
def list_selectable_users(
    current_admin: Dict[str, Any] = Depends(admin_required)
):
    collection = get_selectable_users_collection()

    users = []
    for u in collection.find({"is_active": True}):
        users.append({
            "id": str(u["_id"]),
            "name": u["name"],
            "email": u["email"],
            "is_active": u["is_active"]
        })

    return users



@router.delete("")
def delete_selectable_users(
    request: DeleteSelectableUsersRequest,
    current_admin: Dict[str, Any] = Depends(admin_required)
):
    collection = get_selectable_users_collection()

    if not request.user_ids:
        raise HTTPException(status_code=400, detail="No users selected")

    # Validate ObjectIds
    object_ids = []
    for uid in request.user_ids:
        if not ObjectId.is_valid(uid):
            raise HTTPException(status_code=400, detail=f"Invalid user_id: {uid}")
        object_ids.append(ObjectId(uid))

    # Soft delete (mark inactive)
    result = collection.update_many(
        {"_id": {"$in": object_ids}},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No users found to delete")

    return {
        "success": True,
        "message": f"{result.modified_count} users removed from selectable list",
        "deleted_count": result.modified_count
    }