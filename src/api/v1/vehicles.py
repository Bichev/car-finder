from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from src.core.database import get_database
from src.models.schemas import (
    Vehicle, VehicleLocation,
    PaginationParams, PaginatedResponse
)

router = APIRouter()


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, db=Depends(get_database)):
    """Get vehicle by ID"""
    if not ObjectId.is_valid(vehicle_id):
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    vehicle = await db.vehicles.find_one({"_id": ObjectId(vehicle_id)})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return Vehicle(**vehicle)


@router.get("/", response_model=PaginatedResponse)
async def list_vehicles(
    make: Optional[str] = Query(None, description="Filter by vehicle make"),
    model: Optional[str] = Query(None, description="Filter by vehicle model"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    state: Optional[str] = Query(None, description="Filter by state"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    pagination: PaginationParams = Depends(),
    db=Depends(get_database)
):
    """List vehicles with filtering and pagination"""
    query = {}
    
    if make:
        query["make"] = {"$regex": make, "$options": "i"}
    
    if model:
        query["model"] = {"$regex": model, "$options": "i"}
    
    if year_min or year_max:
        year_query = {}
        if year_min:
            year_query["$gte"] = year_min
        if year_max:
            year_query["$lte"] = year_max
        query["year"] = year_query
    
    if price_min or price_max:
        price_query = {}
        if price_min:
            price_query["$gte"] = price_min
        if price_max:
            price_query["$lte"] = price_max
        query["price"] = price_query
    
    if state:
        query["location.state"] = state.upper()
    
    if source:
        query["source"] = source
    
    if is_active is not None:
        query["is_active"] = is_active
    
    total = await db.vehicles.count_documents(query)
    
    cursor = db.vehicles.find(query).sort("discovered_at", -1).skip(pagination.skip).limit(pagination.limit)
    vehicles = await cursor.to_list(length=pagination.limit)
    
    vehicle_responses = [Vehicle(**vehicle) for vehicle in vehicles]
    
    return PaginatedResponse(
        items=vehicle_responses,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        has_next=(pagination.skip + pagination.limit) < total
    )


@router.get("/search/similar/{vehicle_id}")
async def find_similar_vehicles(
    vehicle_id: str,
    limit: int = Query(10, le=50),
    db=Depends(get_database)
):
    """Find similar vehicles to the given vehicle"""
    if not ObjectId.is_valid(vehicle_id):
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    vehicle = await db.vehicles.find_one({"_id": ObjectId(vehicle_id)})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Find similar vehicles based on make, model, and year range
    query = {
        "_id": {"$ne": ObjectId(vehicle_id)},
        "make": vehicle["make"],
        "model": vehicle["model"],
        "year": {"$gte": vehicle["year"] - 2, "$lte": vehicle["year"] + 2},
        "is_active": True
    }
    
    cursor = db.vehicles.find(query).limit(limit)
    similar_vehicles = await cursor.to_list(length=limit)
    
    return [Vehicle(**v) for v in similar_vehicles]


@router.get("/stats/summary")
async def get_vehicles_summary(db=Depends(get_database)):
    """Get vehicle statistics summary"""
    pipeline = [
        {"$match": {"is_active": True}},
        {
            "$group": {
                "_id": None,
                "total_vehicles": {"$sum": 1},
                "avg_price": {"$avg": "$price"},
                "min_price": {"$min": "$price"},
                "max_price": {"$max": "$price"},
                "avg_year": {"$avg": "$year"},
                "avg_mileage": {"$avg": "$mileage"}
            }
        }
    ]
    
    stats = await db.vehicles.aggregate(pipeline).to_list(length=1)
    
    if not stats:
        return {
            "total_vehicles": 0,
            "avg_price": 0,
            "min_price": 0,
            "max_price": 0,
            "avg_year": 0,
            "avg_mileage": 0
        }
    
    result = stats[0]
    result.pop("_id", None)
    return result


@router.get("/stats/by-make")
async def get_vehicles_by_make(db=Depends(get_database)):
    """Get vehicle count grouped by make"""
    pipeline = [
        {"$match": {"is_active": True}},
        {
            "$group": {
                "_id": "$make",
                "count": {"$sum": 1},
                "avg_price": {"$avg": "$price"},
                "avg_year": {"$avg": "$year"}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    
    stats = await db.vehicles.aggregate(pipeline).to_list(length=20)
    
    return [
        {
            "make": stat["_id"],
            "count": stat["count"],
            "avg_price": round(stat["avg_price"], 2),
            "avg_year": round(stat["avg_year"], 1)
        }
        for stat in stats
    ]


@router.get("/stats/by-state")
async def get_vehicles_by_state(db=Depends(get_database)):
    """Get vehicle count grouped by state"""
    pipeline = [
        {"$match": {"is_active": True}},
        {
            "$group": {
                "_id": "$location.state",
                "count": {"$sum": 1},
                "avg_price": {"$avg": "$price"}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    stats = await db.vehicles.aggregate(pipeline).to_list(length=10)
    
    return [
        {
            "state": stat["_id"],
            "count": stat["count"],
            "avg_price": round(stat["avg_price"], 2)
        }
        for stat in stats
    ]


@router.put("/{vehicle_id}/deactivate")
async def deactivate_vehicle(vehicle_id: str, db=Depends(get_database)):
    """Mark vehicle as inactive (listing no longer available)"""
    if not ObjectId.is_valid(vehicle_id):
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    result = await db.vehicles.update_one(
        {"_id": ObjectId(vehicle_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return {"message": "Vehicle deactivated successfully"} 