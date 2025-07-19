from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from datetime import datetime

from src.core.database import get_database
from src.models.schemas import (
    User, UserCreate, UserUpdate, UserResponse,
    PaginationParams, PaginatedResponse
)

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db=Depends(get_database)):
    """Create a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create new user
    user = User(**user_data.dict())
    user_dict = user.dict(by_alias=True)
    # Remove _id if it's None to let MongoDB generate it
    if "_id" in user_dict and user_dict["_id"] is None:
        del user_dict["_id"]
    result = await db.users.insert_one(user_dict)
    
    # Return created user
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return UserResponse(
        id=str(created_user["_id"]),
        email=created_user["email"],
        subscription_tier=created_user["subscription_tier"],
        alert_preferences=created_user["alert_preferences"],
        created_at=created_user["created_at"]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db=Depends(get_database)):
    """Get user by ID"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        subscription_tier=user["subscription_tier"],
        alert_preferences=user["alert_preferences"],
        created_at=user["created_at"]
    )


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    pagination: PaginationParams = Depends(),
    db=Depends(get_database)
):
    """List all users with pagination"""
    total = await db.users.count_documents({})
    
    cursor = db.users.find({}).skip(pagination.skip).limit(pagination.limit)
    users = await cursor.to_list(length=pagination.limit)
    
    user_responses = [
        UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            subscription_tier=user["subscription_tier"],
            alert_preferences=user["alert_preferences"],
            created_at=user["created_at"]
        )
        for user in users
    ]
    
    return PaginatedResponse(
        items=user_responses,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        has_next=(pagination.skip + pagination.limit) < total
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db=Depends(get_database)
):
    """Update user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Check if user exists
    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    update_data = user_update.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    
    # Return updated user
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        subscription_tier=updated_user["subscription_tier"],
        alert_preferences=updated_user["alert_preferences"],
        created_at=updated_user["created_at"]
    )


@router.delete("/{user_id}")
async def delete_user(user_id: str, db=Depends(get_database)):
    """Delete user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db=Depends(get_database)):
    """Get user by email"""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        subscription_tier=user["subscription_tier"],
        alert_preferences=user["alert_preferences"],
        created_at=user["created_at"]
    ) 