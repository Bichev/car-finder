"""
Search Execution API Endpoints

Endpoints for executing vehicle searches and analyzing opportunities
using Firecrawl and Perplexity integrations.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from loguru import logger

from src.core.database import get_database
from src.services.search_engine import SearchEngine, SearchExecutionResult
from src.services.firecrawl_service import FirecrawlService
from src.services.perplexity_service import PerplexityService
from src.models.schemas import Search, Vehicle, SearchCriteria, OpportunityResponse
from bson import ObjectId

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# Add test models for Swagger UI
class MarketplaceTest(BaseModel):
    """Test configuration for marketplace scraping"""
    marketplace: str = Field(
        default="cars_com",
        description="Marketplace to test",
        example="cars_com"
    )
    make: str = Field(
        default="Honda",
        description="Car make",
        example="Honda"
    )
    model: str = Field(
        default="Accord",
        description="Car model",
        example="Accord"
    )
    year_min: int = Field(
        default=2016,
        description="Minimum year",
        example=2016
    )
    year_max: int = Field(
        default=2021,
        description="Maximum year", 
        example=2021
    )
    price_min: int = Field(
        default=15000,
        description="Minimum price",
        example=15000
    )
    price_max: int = Field(
        default=25000,
        description="Maximum price",
        example=25000
    )
    location_zip: str = Field(
        default="33101",
        description="ZIP code for search",
        example="33101"
    )
    timeout_seconds: int = Field(
        default=30,
        description="API timeout in seconds",
        example=30
    )

class PerplexityTest(BaseModel):
    """Test configuration for Perplexity AI analysis"""
    query: str = Field(
        default="What are the current market trends for 2016-2021 Honda Accord?",
        description="Market analysis question",
        example="What are the current market trends for 2016-2021 Honda Accord?"
    )
    model: str = Field(
        default="sonar-pro",
        description="Perplexity model to use",
        example="sonar-pro"
    )
    max_tokens: int = Field(
        default=500,
        description="Maximum response tokens (shorter = faster)",
        example=500
    )
    timeout_seconds: int = Field(
        default=20,
        description="API timeout in seconds",
        example=20
    )
    context: Optional[str] = Field(
        default="Used car market in Florida",
        description="Additional context for analysis",
        example="Used car market in Florida"
    )


router = APIRouter()


class ExecuteSearchRequest(BaseModel):
    """Request to execute a search"""
    search_id: str = Field(..., description="ID of search configuration to execute")
    force_execution: bool = Field(default=False, description="Force execution even if recently run")


class ExecuteSearchResponse(BaseModel):
    """Response from search execution"""
    message: str
    search_id: str
    execution_id: Optional[str] = None
    vehicles_found: int
    opportunities_created: int
    execution_time: float
    success: bool
    error_message: Optional[str] = None


class AnalyzeVehicleRequest(BaseModel):
    """Request to analyze a single vehicle"""
    vehicle_id: str = Field(..., description="ID of vehicle to analyze")
    include_market_research: bool = Field(default=True, description="Include Perplexity market analysis")


class AnalyzeVehicleResponse(BaseModel):
    """Response from vehicle analysis"""
    vehicle_id: str
    profit_potential: float
    confidence_score: float
    recommended_action: str
    market_analysis: Dict[str, Any]
    cost_breakdown: Dict[str, Any]
    analysis_timestamp: str


class MarketResearchRequest(BaseModel):
    """Request for market research"""
    make: str = Field(..., description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model (optional)")
    year: Optional[int] = Field(None, description="Vehicle year (optional)")
    location: Optional[str] = Field("FL", description="Target location state")


class MarketResearchResponse(BaseModel):
    """Response from market research"""
    make: str
    model: Optional[str]
    year: Optional[int]
    location: str
    market_trends: Dict[str, Any]
    average_pricing: Dict[str, Any]
    regional_insights: List[str]
    research_timestamp: str


@router.post("/execute", response_model=ExecuteSearchResponse)
async def execute_search(
    request: ExecuteSearchRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Execute a search configuration to find and analyze vehicle opportunities
    
    This endpoint:
    1. Scrapes vehicle listings using Firecrawl
    2. Analyzes opportunities using Perplexity AI
    3. Saves results to database
    4. Returns execution summary
    """
    try:
        # Get search configuration
        if not ObjectId.is_valid(request.search_id):
            raise HTTPException(status_code=400, detail="Invalid search ID format")
        
        search_doc = await db.searches.find_one({"_id": ObjectId(request.search_id)})
        if not search_doc:
            raise HTTPException(status_code=404, detail="Search configuration not found")
        
        # Convert ObjectId to string for Pydantic compatibility
        search_doc["_id"] = str(search_doc["_id"])
        search = Search(**search_doc)
        
        # Check if search was recently executed (unless forced)
        if not request.force_execution and search.last_executed:
            from datetime import datetime, timedelta
            if datetime.utcnow() - search.last_executed < timedelta(hours=1):
                raise HTTPException(
                    status_code=429, 
                    detail="Search was executed recently. Use force_execution=true to override."
                )
        
        # Initialize search engine
        search_engine = SearchEngine()
        await search_engine.initialize()
        
        # Execute search in background for long-running operations
        if request.force_execution:
            # Run synchronously for immediate response
            result = await search_engine.execute_search(search)
        else:
            # Run in background
            background_tasks.add_task(_execute_search_background, search_engine, search)
            return ExecuteSearchResponse(
                message="Search execution started in background",
                search_id=request.search_id,
                vehicles_found=0,
                opportunities_created=0,
                execution_time=0.0,
                success=True
            )
        
        await search_engine.close()
        
        return ExecuteSearchResponse(
            message="Search execution completed successfully",
            search_id=request.search_id,
            vehicles_found=result.vehicles_found,
            opportunities_created=result.opportunities_created,
            execution_time=result.execution_time,
            success=result.success,
            error_message=result.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search execution failed: {str(e)}")


@router.post("/analyze-vehicle", response_model=AnalyzeVehicleResponse)
async def analyze_vehicle(
    request: AnalyzeVehicleRequest,
    db=Depends(get_database)
):
    """
    Analyze a single vehicle for profit potential using Perplexity AI
    
    This endpoint provides detailed market analysis and opportunity scoring
    for a specific vehicle listing.
    """
    try:
        # Get vehicle
        if not ObjectId.is_valid(request.vehicle_id):
            raise HTTPException(status_code=400, detail="Invalid vehicle ID format")
        
        vehicle_doc = await db.vehicles.find_one({"_id": ObjectId(request.vehicle_id)})
        if not vehicle_doc:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        vehicle = Vehicle(**vehicle_doc)
        
        # Initialize search engine for analysis
        search_engine = SearchEngine()
        await search_engine.initialize()
        
        # Analyze vehicle
        opportunity_score = await search_engine.analyze_single_vehicle(vehicle)
        
        await search_engine.close()
        
        return AnalyzeVehicleResponse(
            vehicle_id=request.vehicle_id,
            profit_potential=opportunity_score.profit_potential,
            confidence_score=opportunity_score.confidence_score,
            recommended_action=opportunity_score.recommended_action,
            market_analysis=opportunity_score.market_analysis.dict(),
            cost_breakdown=opportunity_score.cost_breakdown.dict(),
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing vehicle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vehicle analysis failed: {str(e)}")


@router.post("/market-research", response_model=MarketResearchResponse)
async def conduct_market_research(
    request: MarketResearchRequest
):
    """
    Conduct market research using Perplexity AI for specific vehicle types
    
    Get market trends, pricing insights, and regional factors for vehicle
    makes/models to inform search configuration decisions.
    """
    try:
        # Initialize Perplexity service
        perplexity = PerplexityService()
        
        # Conduct market research
        market_trends = await perplexity.research_market_trends(
            request.make, 
            request.model,
            "6 months"
        )
        
        # If we have year information, get more specific insights
        if request.year:
            # Create a mock vehicle for analysis
            mock_vehicle = Vehicle(
                source="research",
                external_id="mock",
                make=request.make,
                model=request.model or "Unknown",
                year=request.year,
                mileage=50000,  # Average mileage
                price=20000,   # Average price
                location={"city": "Research", "state": request.location},
                url="",
                last_seen_at=datetime.utcnow()
            )
            
            market_insight = await perplexity.analyze_vehicle_market(mock_vehicle, request.location)
            average_pricing = {
                "value_range": market_insight.market_value_range,
                "market_conditions": market_insight.market_conditions
            }
            regional_insights = market_insight.regional_factors
        else:
            average_pricing = {"note": "Specify year for detailed pricing analysis"}
            regional_insights = ["General market research completed"]
        
        await perplexity.close()
        
        return MarketResearchResponse(
            make=request.make,
            model=request.model,
            year=request.year,
            location=request.location,
            market_trends=market_trends,
            average_pricing=average_pricing,
            regional_insights=regional_insights,
            research_timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error conducting market research: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market research failed: {str(e)}")


@router.get("/search/{search_id}/results")
async def get_search_results(
    search_id: str,
    limit: int = 20,
    db=Depends(get_database)
):
    """
    Get results from a search execution
    
    Returns opportunities and associated vehicles found by the search.
    """
    try:
        if not ObjectId.is_valid(search_id):
            raise HTTPException(status_code=400, detail="Invalid search ID format")
        
        # Check if search exists
        search_doc = await db.searches.find_one({"_id": ObjectId(search_id)})
        if not search_doc:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Initialize search engine
        search_engine = SearchEngine()
        await search_engine.initialize()
        
        # Get results
        results = await search_engine.get_search_results(search_id, limit)
        
        await search_engine.close()
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get search results: {str(e)}")


@router.get("/marketplace-status")
async def get_marketplace_status():
    """
    Get status of configured marketplaces and API services
    
    Returns health status of Firecrawl and Perplexity integrations.
    """
    try:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Test Firecrawl service
        try:
            firecrawl = FirecrawlService()
            # Simple test - this would need to be implemented in the service
            status["services"]["firecrawl"] = {
                "status": "configured",
                "api_key_present": bool(firecrawl.api_key),
                "marketplaces": list(firecrawl.marketplaces.keys())
            }
            await firecrawl.close()
        except Exception as e:
            status["services"]["firecrawl"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test Perplexity service
        try:
            perplexity = PerplexityService()
            status["services"]["perplexity"] = {
                "status": "configured",
                "api_key_present": bool(perplexity.api_key),
                "model": perplexity.model
            }
            await perplexity.close()
        except Exception as e:
            status["services"]["perplexity"] = {
                "status": "error", 
                "error": str(e)
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting marketplace status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/debug-firecrawl")
async def debug_firecrawl():
    """
    Debug Firecrawl integration with detailed logging
    
    This endpoint provides detailed information about Firecrawl requests
    and responses to help debug integration issues.
    """
    try:
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "debug_info": {}
        }
        
        # Test Firecrawl with detailed logging
        try:
            firecrawl = FirecrawlService()
            
            # Create test search criteria
            test_criteria = SearchCriteria(
                makes=["Honda"],
                models=["Accord"],
                year_min=2016,
                year_max=2021,
                price_min=15000,
                price_max=25000,
                locations=["FL"]
            )
            
            logger.info("🔥 DEBUG: Starting Firecrawl test with Cars.com...")
            
            # Test Cars.com (confirmed working in playground)
            cars_url = firecrawl._build_search_url("cars_com", test_criteria, "33101")
            logger.info(f"🔥 DEBUG: Built URL for Cars.com: {cars_url}")
            
            test_result = await firecrawl.search_marketplace("cars_com", test_criteria, "33101")
            
            # Get raw content for debugging extraction
            raw_content = test_result.raw_content if test_result.raw_content else ""
            
            results["debug_info"]["cars_com"] = {
                "url_built": cars_url,
                "api_key_present": bool(firecrawl.api_key),
                "api_key_length": len(firecrawl.api_key) if firecrawl.api_key else 0,
                "success": test_result.success,
                "vehicles_found": test_result.total_found,
                "error": test_result.error_message,
                "source": test_result.source,
                "content_preview": raw_content[:500] if raw_content else None
            }
            
            logger.info(f"🔥 DEBUG: Cars.com result: {test_result.success}, vehicles: {test_result.total_found}")
            if raw_content:
                logger.info(f"🔥 DEBUG: Content preview: {raw_content[:200]}...")
            
            await firecrawl.close()
            
        except Exception as e:
            logger.error(f"🔥 DEBUG: Firecrawl error: {str(e)}")
            results["debug_info"]["error"] = str(e)
        
        return results
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")


@router.post("/test-integration")
async def test_integration():
    """
    Test the integration between Firecrawl and Perplexity services
    
    Performs a small test to ensure both services are working correctly.
    """
    try:
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {}
        }
        
        # Test Firecrawl with a simple query
        try:
            firecrawl = FirecrawlService()
            
            # Create test search criteria
            test_criteria = SearchCriteria(
                makes=["Toyota"],
                models=["Camry"],
                year_min=2015,
                year_max=2020,
                price_min=15000,
                price_max=25000,
                locations=["FL"]
            )
            
            # Test one marketplace (limit to avoid costs)
            test_result = await firecrawl.search_marketplace("edmunds", test_criteria, "33101")
            
            results["tests"]["firecrawl"] = {
                "status": "success" if test_result.success else "failed",
                "marketplace": "edmunds",
                "vehicles_found": test_result.total_found,
                "error": test_result.error_message
            }
            
            await firecrawl.close()
            
        except Exception as e:
            results["tests"]["firecrawl"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test Perplexity with market research
        try:
            perplexity = PerplexityService()
            
            # Simple market research query
            market_trends = await perplexity.research_market_trends("Toyota", "Camry", "3 months")
            
            results["tests"]["perplexity"] = {
                "status": "success",
                "trends_analyzed": bool(market_trends.get("trend_direction")),
                "confidence": market_trends.get("confidence", 0.0)
            }
            
            await perplexity.close()
            
        except Exception as e:
            results["tests"]["perplexity"] = {
                "status": "error",
                "error": str(e)
            }
        
        return results
        
    except Exception as e:
        logger.error(f"Error testing integration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integration test failed: {str(e)}")


@router.post("/test-perplexity")
async def test_perplexity():
    """
    Direct Perplexity test to see AI analysis output
    
    This endpoint makes a simple Perplexity call and returns the full AI response
    so you can see exactly what the AI analysis looks like.
    """
    try:
        from src.services.perplexity_service import PerplexityService
        
        perplexity = PerplexityService()
        
        # Simple test query
        query = "What are the current market trends for 2016-2021 Honda Accord in the used car market? Include pricing insights and depreciation patterns."
        
        logger.info(f"🧠 PERPLEXITY: Testing with query: {query[:100]}...")
        
        # Make direct API call
        response = await perplexity._query_perplexity(
            query=query,
            system_prompt="You are a car market analyst. Provide detailed insights about vehicle pricing and market trends."
        )
        
        await perplexity.close()
        
        return {
            "query": query,
            "ai_response": response.get("content", "No response"),
            "model_used": "sonar-pro",
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"🧠 PERPLEXITY: Test error: {str(e)}")
        return {
            "query": query if 'query' in locals() else "Unknown",
            "ai_response": f"Error: {str(e)}",
            "model_used": "sonar-pro",
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/test/firecrawl", 
    summary="🔥 Test Firecrawl Scraping",
    description="Interactive test for Firecrawl vehicle scraping with customizable parameters",
    tags=["🧪 Interactive Tests"])
async def test_firecrawl_interactive(test_config: MarketplaceTest):
    """
    Test Firecrawl scraping with customizable parameters.
    
    **Try different combinations:**
    - **Marketplaces**: cars_com, edmunds, cargurus  
    - **Cars**: Honda Accord, Toyota Camry, BMW 3 Series
    - **Price ranges**: $10k-20k, $20k-30k, $30k+
    - **Years**: 2015-2020, 2018-2023, etc.
    """
    try:
        from src.services.firecrawl_service import FirecrawlService
        
        firecrawl = FirecrawlService()
        
        # Build test criteria
        criteria = SearchCriteria(
            makes=[test_config.make],
            models=[test_config.model],
            year_min=test_config.year_min,
            year_max=test_config.year_max,
            price_min=test_config.price_min,
            price_max=test_config.price_max,
            locations=["FL"]
        )
        
        logger.info(f"🔥 Testing {test_config.marketplace} for {test_config.make} {test_config.model}")
        
        # Test with custom timeout
        start_time = datetime.utcnow()
        result = await firecrawl.search_marketplace(
            test_config.marketplace, 
            criteria, 
            test_config.location_zip
        )
        end_time = datetime.utcnow()
        
        await firecrawl.close()
        
        return {
            "marketplace": test_config.marketplace,
            "search_criteria": {
                "make": test_config.make,
                "model": test_config.model,
                "year_range": f"{test_config.year_min}-{test_config.year_max}",
                "price_range": f"${test_config.price_min:,}-${test_config.price_max:,}",
                "location": test_config.location_zip
            },
            "results": {
                "success": result.success,
                "vehicles_found": result.total_found,
                "sample_vehicles": result.vehicles[:3] if result.vehicles else [],
                "error": result.error_message
            },
            "performance": {
                "duration_seconds": (end_time - start_time).total_seconds(),
                "status": "✅ Fast" if (end_time - start_time).total_seconds() < 15 else "⏳ Slow"
            },
            "content_preview": result.raw_content[:300] if hasattr(result, 'raw_content') and result.raw_content else None
        }
        
    except Exception as e:
        logger.error(f"🔥 Firecrawl test error: {str(e)}")
        return {
            "marketplace": test_config.marketplace,
            "error": str(e),
            "success": False
        }

@router.post("/test/perplexity",
    summary="🧠 Test Perplexity AI Analysis", 
    description="Interactive test for Perplexity AI market analysis with customizable parameters",
    tags=["🧪 Interactive Tests"])
async def test_perplexity_interactive(test_config: PerplexityTest):
    """
    Test Perplexity AI analysis with customizable parameters.
    
    **Try different queries:**
    - **Market trends**: "What are Honda Accord pricing trends?"
    - **Comparisons**: "Compare Honda Accord vs Toyota Camry value"
    - **Predictions**: "Will Tesla Model 3 prices drop in 2024?"
    - **Regional**: "Best car deals in Florida vs California"
    
    **Adjust max_tokens for speed:**
    - **Fast (200 tokens)**: Quick insights, ~10 seconds
    - **Medium (500 tokens)**: Detailed analysis, ~20 seconds  
    - **Detailed (1000 tokens)**: Comprehensive report, ~30 seconds
    """
    try:
        from src.services.perplexity_service import PerplexityService
        
        perplexity = PerplexityService()
        
        logger.info(f"🧠 Testing Perplexity: {test_config.query[:50]}...")
        
        start_time = datetime.utcnow()
        
        # Custom API call with user parameters
        response = await perplexity._query_perplexity(
            query=test_config.query,
            system_prompt="You are an expert automotive market analyst. Provide clear, data-driven insights.",
            max_tokens=test_config.max_tokens
        )
        
        end_time = datetime.utcnow()
        await perplexity.close()
        
        # Parse response according to Perplexity API format
        if response.get("success") and response.get("data"):
            api_data = response["data"]
            content = api_data.get("choices", [{}])[0].get("message", {}).get("content", "No response received")
            usage = api_data.get("usage", {})
            citations = api_data.get("citations", [])
        else:
            content = f"API Error: {response.get('error', 'Unknown error')}"
            usage = {}
            citations = []
        
        return {
            "query": test_config.query,
            "configuration": {
                "model": test_config.model,
                "max_tokens": test_config.max_tokens,
                "context": test_config.context
            },
            "ai_analysis": content,
            "citations": citations[:5],  # Show first 5 citations
            "performance": {
                "duration_seconds": (end_time - start_time).total_seconds(),
                "tokens_used": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "status": "✅ Fast" if (end_time - start_time).total_seconds() < 15 else "⏳ Slow"
            },
            "metadata": {
                "success": response.get("success", False),
                "model_used": test_config.model,
                "timestamp": end_time.isoformat(),
                "api_response_format": "perplexity_chat_completions"
            }
        }
        
    except Exception as e:
        logger.error(f"🧠 Perplexity test error: {str(e)}")
        return {
            "query": test_config.query,
            "ai_analysis": f"Error: {str(e)}",
            "performance": {"status": "❌ Failed"},
            "metadata": {"success": False}
        }

@router.post("/test/combined",
    summary="🚀 Combined Test: Firecrawl + Perplexity",
    description="Test complete workflow: scrape vehicles + AI analysis",
    tags=["🧪 Interactive Tests"])
async def test_combined_workflow(
    marketplace_config: MarketplaceTest,
    analysis_query: str = "Analyze the market value and trends for these vehicles"
):
    """
    Complete workflow test: Find vehicles + AI market analysis.
    
    **Perfect for testing:**
    - End-to-end functionality
    - Performance of full pipeline  
    - Real-world use cases
    """
    try:
        results = {
            "workflow": "firecrawl_then_perplexity",
            "steps": {}
        }
        
        # Step 1: Firecrawl
        step1_start = datetime.utcnow()
        firecrawl_result = await test_firecrawl_interactive(marketplace_config)
        step1_end = datetime.utcnow()
        
        results["steps"]["1_firecrawl"] = {
            "duration_seconds": (step1_end - step1_start).total_seconds(),
            "vehicles_found": firecrawl_result.get("results", {}).get("vehicles_found", 0),
            "success": firecrawl_result.get("results", {}).get("success", False)
        }
        
        # Step 2: Perplexity (only if vehicles found)
        if results["steps"]["1_firecrawl"]["vehicles_found"] > 0:
            enhanced_query = f"{analysis_query}. Found {results['steps']['1_firecrawl']['vehicles_found']} {marketplace_config.make} {marketplace_config.model} vehicles in ${marketplace_config.price_min:,}-${marketplace_config.price_max:,} range."
            
            perplexity_config = PerplexityTest(
                query=enhanced_query,
                max_tokens=300,  # Shorter for combined test
                timeout_seconds=20
            )
            
            step2_start = datetime.utcnow()
            perplexity_result = await test_perplexity_interactive(perplexity_config)
            step2_end = datetime.utcnow()
            
            results["steps"]["2_perplexity"] = {
                "duration_seconds": (step2_end - step2_start).total_seconds(),
                "analysis": perplexity_result.get("ai_analysis", "No analysis"),
                "success": perplexity_result.get("metadata", {}).get("success", False)
            }
        else:
            results["steps"]["2_perplexity"] = {
                "skipped": "No vehicles found to analyze"
            }
        
        return {
            "summary": {
                "total_duration": sum([
                    results["steps"]["1_firecrawl"]["duration_seconds"],
                    results["steps"].get("2_perplexity", {}).get("duration_seconds", 0)
                ]),
                "vehicles_found": results["steps"]["1_firecrawl"]["vehicles_found"],
                "analysis_provided": "2_perplexity" in results["steps"] and results["steps"]["2_perplexity"].get("success", False)
            },
            "detailed_results": results,
            "firecrawl_data": firecrawl_result,
            "ai_analysis": results["steps"].get("2_perplexity", {}).get("analysis")
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}


async def _execute_search_background(search_engine: SearchEngine, search: Search):
    """Background task for search execution"""
    try:
        logger.info(f"Starting background search execution for: {search.name}")
        result = await search_engine.execute_search(search)
        logger.info(f"Background search completed: {result.success}")
    except Exception as e:
        logger.error(f"Background search execution failed: {str(e)}")
    finally:
        await search_engine.close()


# Add datetime import
from datetime import datetime 