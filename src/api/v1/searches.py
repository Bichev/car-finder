from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from src.core.database import get_database
from src.models.schemas import (
    Search, SearchCreate, SearchUpdate, SearchResponse,
    PaginationParams, PaginatedResponse
)

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def create_search(
    search_data: SearchCreate,
    user_id: str = Query(..., description="User ID who owns this search"),
    db=Depends(get_database)
):
    """Create a new search configuration"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Check if user exists
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check user's search limit based on subscription tier
    user_searches = await db.searches.count_documents({"user_id": user_id, "is_active": True})
    
    max_searches = {
        "starter": 5,
        "professional": 25,
        "enterprise": 100
    }
    
    tier_limit = max_searches.get(user["subscription_tier"], 5)
    if user_searches >= tier_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum searches limit ({tier_limit}) reached for {user['subscription_tier']} tier"
        )
    
    # Create new search
    search = Search(user_id=user_id, **search_data.dict())
    search_dict = search.dict(by_alias=True)
    # Remove _id if it's None to let MongoDB generate it
    if "_id" in search_dict and search_dict["_id"] is None:
        del search_dict["_id"]
    result = await db.searches.insert_one(search_dict)
    
    # Return created search
    created_search = await db.searches.find_one({"_id": result.inserted_id})
    return SearchResponse(
        id=str(created_search["_id"]),
        name=created_search["name"],
        criteria=created_search["criteria"],
        schedule_cron=created_search["schedule_cron"],
        is_active=created_search["is_active"],
        last_executed=created_search.get("last_executed"),
        created_at=created_search["created_at"]
    )


@router.get("/{search_id}", response_model=SearchResponse)
async def get_search(search_id: str, db=Depends(get_database)):
    """Get search by ID"""
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")
    
    search = await db.searches.find_one({"_id": ObjectId(search_id)})
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    return SearchResponse(
        id=str(search["_id"]),
        name=search["name"],
        criteria=search["criteria"],
        schedule_cron=search["schedule_cron"],
        is_active=search["is_active"],
        last_executed=search.get("last_executed"),
        created_at=search["created_at"]
    )


@router.get("/", response_model=PaginatedResponse)
async def list_searches(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    pagination: PaginationParams = Depends(),
    db=Depends(get_database)
):
    """List searches with optional filtering"""
    query = {}
    
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        query["user_id"] = ObjectId(user_id)
    
    if is_active is not None:
        query["is_active"] = is_active
    
    total = await db.searches.count_documents(query)
    
    cursor = db.searches.find(query).skip(pagination.skip).limit(pagination.limit)
    searches = await cursor.to_list(length=pagination.limit)
    
    search_responses = [
        SearchResponse(
            id=str(search["_id"]),
            name=search["name"],
            criteria=search["criteria"],
            schedule_cron=search["schedule_cron"],
            is_active=search["is_active"],
            last_executed=search.get("last_executed"),
            created_at=search["created_at"]
        )
        for search in searches
    ]
    
    return PaginatedResponse(
        items=search_responses,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        has_next=(pagination.skip + pagination.limit) < total
    )


@router.put("/{search_id}", response_model=SearchResponse)
async def update_search(
    search_id: str,
    search_update: SearchUpdate,
    db=Depends(get_database)
):
    """Update search configuration"""
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")
    
    # Check if search exists
    existing_search = await db.searches.find_one({"_id": ObjectId(search_id)})
    if not existing_search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Update search
    update_data = search_update.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.searches.update_one(
            {"_id": ObjectId(search_id)},
            {"$set": update_data}
        )
    
    # Return updated search
    updated_search = await db.searches.find_one({"_id": ObjectId(search_id)})
    return SearchResponse(
        id=str(updated_search["_id"]),
        name=updated_search["name"],
        criteria=updated_search["criteria"],
        schedule_cron=updated_search["schedule_cron"],
        is_active=updated_search["is_active"],
        last_executed=updated_search.get("last_executed"),
        created_at=updated_search["created_at"]
    )


@router.delete("/{search_id}")
async def delete_search(search_id: str, db=Depends(get_database)):
    """Delete search configuration"""
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")
    
    result = await db.searches.delete_one({"_id": ObjectId(search_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Search not found")
    
    return {"message": "Search deleted successfully"}


@router.post("/{search_id}/execute")
async def execute_search(search_id: str, db=Depends(get_database)):
    """Manually execute a search"""
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID")
    
    search = await db.searches.find_one({"_id": ObjectId(search_id)})
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    if not search["is_active"]:
        raise HTTPException(status_code=400, detail="Search is not active")
    
    # TODO: Trigger search execution via Celery task
    # For now, just update the last_executed timestamp
    await db.searches.update_one(
        {"_id": ObjectId(search_id)},
        {"$set": {"last_executed": datetime.utcnow()}}
    )
    
    return {"message": "Search execution triggered successfully"}


@router.get("/user/{user_id}/active", response_model=List[SearchResponse])
async def get_user_active_searches(user_id: str, db=Depends(get_database)):
    """Get all active searches for a user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    cursor = db.searches.find({
        "user_id": ObjectId(user_id),
        "is_active": True
    })
    searches = await cursor.to_list(length=None)
    
    return [
        SearchResponse(
            id=str(search["_id"]),
            name=search["name"],
            criteria=search["criteria"],
            schedule_cron=search["schedule_cron"],
            is_active=search["is_active"],
            last_executed=search.get("last_executed"),
            created_at=search["created_at"]
        )
        for search in searches
    ] 