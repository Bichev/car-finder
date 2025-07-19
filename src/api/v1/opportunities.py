from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from src.core.database import get_database
from src.models.schemas import (
    Opportunity, OpportunityResponse, OpportunityStatus,
    PaginationParams, PaginatedResponse
)

router = APIRouter()


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: str, db=Depends(get_database)):
    """Get opportunity by ID"""
    if not ObjectId.is_valid(opportunity_id):
        raise HTTPException(status_code=400, detail="Invalid opportunity ID")
    
    # Get opportunity with vehicle data
    pipeline = [
        {"$match": {"_id": ObjectId(opportunity_id)}},
        {
            "$lookup": {
                "from": "vehicles",
                "localField": "vehicle_id",
                "foreignField": "_id",
                "as": "vehicle"
            }
        },
        {"$unwind": "$vehicle"}
    ]
    
    opportunities = await db.opportunities.aggregate(pipeline).to_list(length=1)
    if not opportunities:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opportunity = opportunities[0]
    
    return OpportunityResponse(
        id=str(opportunity["_id"]),
        vehicle=opportunity["vehicle"],
        market_analysis=opportunity["market_analysis"],
        cost_breakdown=opportunity["cost_breakdown"],
        projected_profit=opportunity["projected_profit"],
        confidence_score=opportunity["confidence_score"],
        status=opportunity["status"],
        created_at=opportunity["created_at"]
    )


@router.get("/", response_model=PaginatedResponse)
async def list_opportunities(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[OpportunityStatus] = Query(None, description="Filter by status"),
    min_profit: Optional[float] = Query(None, description="Minimum projected profit"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    pagination: PaginationParams = Depends(),
    db=Depends(get_database)
):
    """List opportunities with filtering and pagination"""
    match_query = {}
    
    if status:
        match_query["status"] = status
    
    if min_profit:
        match_query["projected_profit"] = {"$gte": min_profit}
    
    if min_confidence:
        match_query["confidence_score"] = {"$gte": min_confidence}
    
    # If user_id is provided, filter by searches belonging to that user
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Get all search IDs for the user
        user_searches = await db.searches.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        search_ids = [search["_id"] for search in user_searches]
        match_query["search_id"] = {"$in": search_ids}
    
    # Count total documents
    total = await db.opportunities.count_documents(match_query)
    
    # Build aggregation pipeline
    pipeline = [
        {"$match": match_query},
        {"$sort": {"confidence_score": -1, "projected_profit": -1, "created_at": -1}},
        {"$skip": pagination.skip},
        {"$limit": pagination.limit},
        {
            "$lookup": {
                "from": "vehicles",
                "localField": "vehicle_id",
                "foreignField": "_id",
                "as": "vehicle"
            }
        },
        {"$unwind": "$vehicle"}
    ]
    
    opportunities = await db.opportunities.aggregate(pipeline).to_list(length=pagination.limit)
    
    opportunity_responses = [
        OpportunityResponse(
            id=str(opp["_id"]),
            vehicle=opp["vehicle"],
            market_analysis=opp["market_analysis"],
            cost_breakdown=opp["cost_breakdown"],
            projected_profit=opp["projected_profit"],
            confidence_score=opp["confidence_score"],
            status=opp["status"],
            created_at=opp["created_at"]
        )
        for opp in opportunities
    ]
    
    return PaginatedResponse(
        items=opportunity_responses,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        has_next=(pagination.skip + pagination.limit) < total
    )


@router.put("/{opportunity_id}/status")
async def update_opportunity_status(
    opportunity_id: str,
    status: OpportunityStatus,
    db=Depends(get_database)
):
    """Update opportunity status"""
    if not ObjectId.is_valid(opportunity_id):
        raise HTTPException(status_code=400, detail="Invalid opportunity ID")
    
    result = await db.opportunities.update_one(
        {"_id": ObjectId(opportunity_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return {"message": "Opportunity status updated successfully"}


@router.get("/stats/summary")
async def get_opportunities_summary(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db=Depends(get_database)
):
    """Get opportunities summary statistics"""
    match_query = {}
    
    # If user_id is provided, filter by searches belonging to that user
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        user_searches = await db.searches.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        search_ids = [search["_id"] for search in user_searches]
        match_query["search_id"] = {"$in": search_ids}
    
    # Aggregate statistics
    pipeline = [
        {"$match": match_query},
        {
            "$group": {
                "_id": None,
                "total_opportunities": {"$sum": 1},
                "avg_profit": {"$avg": "$projected_profit"},
                "max_profit": {"$max": "$projected_profit"},
                "avg_confidence": {"$avg": "$confidence_score"},
                "high_confidence_count": {
                    "$sum": {"$cond": [{"$gte": ["$confidence_score", 0.8]}, 1, 0]}
                }
            }
        }
    ]
    
    stats = await db.opportunities.aggregate(pipeline).to_list(length=1)
    
    if not stats:
        return {
            "total_opportunities": 0,
            "avg_profit": 0,
            "max_profit": 0,
            "avg_confidence": 0,
            "high_confidence_count": 0
        }
    
    result = stats[0]
    result.pop("_id", None)
    return result


@router.get("/top/{limit}")
async def get_top_opportunities(
    limit: int = 10,
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db=Depends(get_database)
):
    """Get top opportunities by confidence and profit"""
    match_query = {"status": {"$in": ["new", "alerted"]}}
    
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        user_searches = await db.searches.find({"user_id": ObjectId(user_id)}).to_list(length=None)
        search_ids = [search["_id"] for search in user_searches]
        match_query["search_id"] = {"$in": search_ids}
    
    pipeline = [
        {"$match": match_query},
        {"$sort": {"confidence_score": -1, "projected_profit": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "vehicles",
                "localField": "vehicle_id",
                "foreignField": "_id",
                "as": "vehicle"
            }
        },
        {"$unwind": "$vehicle"}
    ]
    
    opportunities = await db.opportunities.aggregate(pipeline).to_list(length=limit)
    
    return [
        OpportunityResponse(
            id=str(opp["_id"]),
            vehicle=opp["vehicle"],
            market_analysis=opp["market_analysis"],
            cost_breakdown=opp["cost_breakdown"],
            projected_profit=opp["projected_profit"],
            confidence_score=opp["confidence_score"],
            status=opp["status"],
            created_at=opp["created_at"]
        )
        for opp in opportunities
    ] 