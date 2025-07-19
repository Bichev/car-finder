"""
Search Engine Service

This service orchestrates the complete vehicle search and analysis workflow,
coordinating Firecrawl data collection with Perplexity market analysis.
"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.core.database import get_database
from src.services.firecrawl_service import FirecrawlService, ScrapingResult
from src.services.perplexity_service import PerplexityService, MarketInsight
from src.models.schemas import (
    Vehicle, VehicleLocation, SearchCriteria, Search, 
    Opportunity, MarketAnalysis, CostBreakdown, OpportunityStatus
)
from src.core.config import settings


@dataclass 
class SearchExecutionResult:
    """Result of executing a search"""
    search_id: str
    vehicles_found: int
    opportunities_created: int
    execution_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class OpportunityScore:
    """Opportunity scoring result"""
    vehicle_id: str
    profit_potential: float
    confidence_score: float
    market_analysis: MarketAnalysis
    cost_breakdown: CostBreakdown
    recommended_action: str


class SearchEngine:
    """Main search engine coordinating vehicle discovery and analysis"""
    
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.perplexity = PerplexityService()
        self.database = None
        
    async def initialize(self):
        """Initialize database connection"""
        self.database = get_database()
    
    async def execute_search(self, search: Search) -> SearchExecutionResult:
        """
        Execute a complete search workflow
        
        Args:
            search: Search configuration to execute
            
        Returns:
            SearchExecutionResult with execution details
        """
        start_time = datetime.utcnow()
        logger.info(f"Executing search: {search.name}")
        
        try:
            # 1. Scrape vehicles from marketplaces
            logger.info("Step 1: Scraping vehicle listings...")
            scraping_results = await self.firecrawl.search_all_marketplaces(
                search.criteria,
                self._get_target_zip_codes(search.criteria.locations)
            )
            
            # 2. Process and save vehicles
            logger.info("Step 2: Processing vehicle data...")
            vehicles_saved = await self._process_scraped_vehicles(scraping_results, search.id)
            
            # 3. Analyze opportunities
            logger.info("Step 3: Analyzing market opportunities...")
            opportunities_created = await self._analyze_opportunities(search)
            
            # 4. Update search execution time
            await self._update_search_execution(search.id)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Search completed: {vehicles_saved} vehicles, {opportunities_created} opportunities")
            
            return SearchExecutionResult(
                search_id=search.id,
                vehicles_found=vehicles_saved,
                opportunities_created=opportunities_created,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Search execution failed: {str(e)}")
            
            return SearchExecutionResult(
                search_id=search.id,
                vehicles_found=0,
                opportunities_created=0,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def analyze_single_vehicle(self, vehicle: Vehicle, search_criteria: SearchCriteria = None) -> OpportunityScore:
        """
        Analyze a single vehicle for opportunity potential
        
        Args:
            vehicle: Vehicle to analyze
            search_criteria: Optional search criteria for context
            
        Returns:
            OpportunityScore with detailed analysis
        """
        try:
            logger.info(f"Analyzing vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
            
            # Get market analysis from Perplexity
            market_insight = await self.perplexity.analyze_vehicle_market(
                vehicle, 
                vehicle.location.state if vehicle.location else None
            )
            
            # Get competitive pricing
            competitive_analysis = await self.perplexity.get_competitive_pricing(vehicle)
            
            # Calculate costs
            cost_breakdown = self._calculate_acquisition_costs(vehicle)
            
            # Build market analysis object
            market_analysis = MarketAnalysis(
                kbb_value=market_insight.market_value_range.get("average") if market_insight.market_value_range else None,
                edmunds_value=None,  # We could add KBB/Edmunds API integration later
                perplexity_insights={
                    "market_conditions": market_insight.market_conditions,
                    "regional_factors": market_insight.regional_factors,
                    "confidence_score": market_insight.confidence_score,
                    "sources": market_insight.sources
                },
                comparable_prices=[competitive_analysis.average_market_price],
                market_average=competitive_analysis.average_market_price
            )
            
            # Calculate profit potential
            profit_potential = self._calculate_profit_potential(
                vehicle, 
                market_analysis, 
                cost_breakdown
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                vehicle,
                market_analysis,
                competitive_analysis,
                market_insight
            )
            
            # Determine recommended action
            recommended_action = self._get_recommendation(
                profit_potential, 
                confidence_score, 
                competitive_analysis.market_trend
            )
            
            return OpportunityScore(
                vehicle_id=str(vehicle.id) if vehicle.id else "",
                profit_potential=profit_potential,
                confidence_score=confidence_score,
                market_analysis=market_analysis,
                cost_breakdown=cost_breakdown,
                recommended_action=recommended_action
            )
            
        except Exception as e:
            logger.error(f"Error analyzing vehicle: {str(e)}")
            # Return a low-score result for failed analysis
            return OpportunityScore(
                vehicle_id=str(vehicle.id) if vehicle.id else "",
                profit_potential=0.0,
                confidence_score=0.0,
                market_analysis=MarketAnalysis(
                    comparable_prices=[vehicle.price],
                    market_average=vehicle.price
                ),
                cost_breakdown=self._calculate_acquisition_costs(vehicle),
                recommended_action="skip"
            )
    
    async def _process_scraped_vehicles(self, scraping_results: List[ScrapingResult], search_id: str) -> int:
        """Process and save scraped vehicles to database"""
        vehicles_saved = 0
        
        for result in scraping_results:
            if not result.success:
                logger.warning(f"Skipping failed scraping result from {result.source}")
                continue
            
            for vehicle_data in result.vehicles:
                try:
                    # Check if vehicle already exists
                    existing = await self.database.vehicles.find_one({
                        "external_id": vehicle_data.get("external_id"),
                        "source": vehicle_data.get("source")
                    })
                    
                    if existing:
                        # Update last_seen_at
                        await self.database.vehicles.update_one(
                            {"_id": existing["_id"]},
                            {"$set": {"last_seen_at": datetime.utcnow()}}
                        )
                        continue
                    
                    # Create new vehicle
                    vehicle = Vehicle(**vehicle_data)
                    vehicle_dict = vehicle.dict(by_alias=True)
                    if "_id" in vehicle_dict and vehicle_dict["_id"] is None:
                        del vehicle_dict["_id"]
                    
                    await self.database.vehicles.insert_one(vehicle_dict)
                    vehicles_saved += 1
                    
                except Exception as e:
                    logger.error(f"Error saving vehicle: {str(e)}")
                    continue
        
        return vehicles_saved
    
    async def _analyze_opportunities(self, search: Search) -> int:
        """Analyze vehicles for opportunities based on search criteria"""
        opportunities_created = 0
        
        # Get recent vehicles matching search criteria
        query = self._build_vehicle_query(search.criteria)
        query["last_seen_at"] = {"$gte": datetime.utcnow() - timedelta(hours=24)}
        
        cursor = self.database.vehicles.find(query).limit(50)  # Limit for cost control
        vehicles = await cursor.to_list(length=50)
        
        for vehicle_data in vehicles:
            try:
                # Convert to Vehicle object
                vehicle = Vehicle(**vehicle_data)
                
                # Analyze opportunity
                opportunity_score = await self.analyze_single_vehicle(vehicle, search.criteria)
                
                # Create opportunity if it meets thresholds
                if self._meets_opportunity_threshold(opportunity_score):
                    opportunity = Opportunity(
                        vehicle_id=opportunity_score.vehicle_id,
                        search_id=search.id,
                        market_analysis=opportunity_score.market_analysis,
                        cost_breakdown=opportunity_score.cost_breakdown,
                        projected_profit=opportunity_score.profit_potential,
                        confidence_score=opportunity_score.confidence_score,
                        status=OpportunityStatus.NEW
                    )
                    
                    opportunity_dict = opportunity.dict(by_alias=True)
                    if "_id" in opportunity_dict and opportunity_dict["_id"] is None:
                        del opportunity_dict["_id"]
                    
                    await self.database.opportunities.insert_one(opportunity_dict)
                    opportunities_created += 1
                    
                    logger.info(f"Created opportunity: ${opportunity_score.profit_potential:.2f} profit, {opportunity_score.confidence_score:.2f} confidence")
                
            except Exception as e:
                logger.error(f"Error analyzing opportunity: {str(e)}")
                continue
        
        return opportunities_created
    
    def _get_target_zip_codes(self, locations: List[str]) -> List[str]:
        """Get ZIP codes for target locations"""
        zip_codes = []
        
        location_zips = {
            "FL": [
                "33101",  # Miami
                "33602",  # Tampa  
                "32801",  # Orlando
                "32301",  # Tallahassee
                "32501",  # Pensacola
                "33901",  # Fort Myers
                "33401",  # West Palm Beach
                "32601",  # Gainesville
            ],
            "GA": [
                "30309",  # Atlanta
                "31401",  # Savannah
                "30901",  # Augusta
                "31201",  # Macon
                "30601",  # Athens
                "31701",  # Albany
                "30501",  # Gainesville, GA
            ]
        }
        
        for location in locations:
            if location.upper() in location_zips:
                zip_codes.extend(location_zips[location.upper()])
        
        return zip_codes or location_zips["FL"]  # Default to FL
    
    def _build_vehicle_query(self, criteria: SearchCriteria) -> Dict[str, Any]:
        """Build MongoDB query from search criteria"""
        query = {"is_active": True}
        
        if criteria.makes:
            query["make"] = {"$in": [make.title() for make in criteria.makes]}
        
        if criteria.models:
            query["model"] = {"$in": [model.title() for model in criteria.models]}
        
        if criteria.year_min or criteria.year_max:
            year_query = {}
            if criteria.year_min:
                year_query["$gte"] = criteria.year_min
            if criteria.year_max:
                year_query["$lte"] = criteria.year_max
            query["year"] = year_query
        
        if criteria.price_min or criteria.price_max:
            price_query = {}
            if criteria.price_min:
                price_query["$gte"] = criteria.price_min
            if criteria.price_max:
                price_query["$lte"] = criteria.price_max
            query["price"] = price_query
        
        if criteria.mileage_max:
            query["mileage"] = {"$lte": criteria.mileage_max}
        
        if criteria.locations:
            query["location.state"] = {"$in": [loc.upper() for loc in criteria.locations]}
        
        return query
    
    def _calculate_acquisition_costs(self, vehicle: Vehicle) -> CostBreakdown:
        """Calculate total acquisition costs for a vehicle"""
        purchase_price = vehicle.price
        
        # State-specific tax rates
        tax_rates = {
            "FL": 0.06,  # 6% sales tax
            "GA": 0.04   # 4% title ad valorem tax
        }
        
        state = vehicle.location.state if vehicle.location else "FL"
        tax_rate = tax_rates.get(state, 0.06)
        
        sales_tax = purchase_price * tax_rate
        
        # Fixed fees by state
        state_fees = {
            "FL": {"title": 77.25, "registration": 225},
            "GA": {"title": 18, "registration": 20}
        }
        
        fees = state_fees.get(state, state_fees["FL"])
        title_fee = fees["title"]
        registration_fee = fees["registration"]
        
        # Transportation cost (estimated)
        base_transport = float(settings.BASE_TRANSPORT_FEE)
        
        # Add distance-based cost if we have location data
        transport_cost = base_transport
        if vehicle.location:
            # Simplified: assume 200 miles average distance
            distance_miles = 200
            cost_per_mile = float(settings.TRANSPORTATION_COST_PER_MILE)
            transport_cost = base_transport + (distance_miles * cost_per_mile)
        
        total_cost = purchase_price + sales_tax + title_fee + registration_fee + transport_cost
        
        return CostBreakdown(
            purchase_price=purchase_price,
            sales_tax=sales_tax,
            title_fee=title_fee,
            registration_fee=registration_fee,
            transportation_cost=transport_cost,
            total_cost=total_cost
        )
    
    def _calculate_profit_potential(self, vehicle: Vehicle, market_analysis: MarketAnalysis, cost_breakdown: CostBreakdown) -> float:
        """Calculate profit potential"""
        # Use market average or perplexity insights for resale estimate
        resale_estimate = market_analysis.market_average
        
        if not resale_estimate and market_analysis.comparable_prices:
            resale_estimate = sum(market_analysis.comparable_prices) / len(market_analysis.comparable_prices)
        
        if not resale_estimate:
            resale_estimate = vehicle.price * 1.1  # Conservative 10% markup fallback
        
        # Calculate profit
        profit = resale_estimate - cost_breakdown.total_cost
        
        return max(profit, 0.0)  # Never negative
    
    def _calculate_confidence_score(self, vehicle: Vehicle, market_analysis: MarketAnalysis, competitive_analysis, market_insight) -> float:
        """Calculate confidence score for the opportunity"""
        confidence = 0.0
        
        # Base score from Perplexity analysis
        if hasattr(market_insight, 'confidence_score'):
            confidence += market_insight.confidence_score * 0.4
        
        # Vehicle data quality
        data_quality = 0.0
        if vehicle.mileage and vehicle.mileage > 0:
            data_quality += 0.2
        if vehicle.year and vehicle.year > 2000:
            data_quality += 0.2
        if vehicle.location and vehicle.location.state:
            data_quality += 0.2
        
        confidence += data_quality * 0.3
        
        # Market trend confidence
        if competitive_analysis.market_trend in ["rising", "stable"]:
            confidence += 0.2
        elif competitive_analysis.market_trend == "falling":
            confidence += 0.05
        
        # Price reasonableness
        if market_analysis.market_average:
            price_ratio = vehicle.price / market_analysis.market_average
            if 0.7 <= price_ratio <= 1.0:  # 70-100% of market value
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_recommendation(self, profit_potential: float, confidence_score: float, market_trend: str) -> str:
        """Get recommendation based on analysis"""
        if profit_potential >= 2000 and confidence_score >= 0.7:
            return "strong_buy"
        elif profit_potential >= 1000 and confidence_score >= 0.5:
            return "consider"
        elif profit_potential >= 500 and confidence_score >= 0.6:
            return "monitor"
        else:
            return "skip"
    
    def _meets_opportunity_threshold(self, opportunity_score: OpportunityScore) -> bool:
        """Check if opportunity meets minimum thresholds"""
        min_profit = 500  # Minimum $500 profit
        min_confidence = 0.3  # Minimum 30% confidence
        
        return (opportunity_score.profit_potential >= min_profit and 
                opportunity_score.confidence_score >= min_confidence)
    
    async def _update_search_execution(self, search_id: str):
        """Update search last execution time"""
        await self.database.searches.update_one(
            {"_id": search_id},
            {"$set": {"last_executed": datetime.utcnow()}}
        )
    
    async def get_search_results(self, search_id: str, limit: int = 20) -> Dict[str, Any]:
        """Get results for a specific search"""
        # Get opportunities for this search
        cursor = self.database.opportunities.find(
            {"search_id": search_id}
        ).sort("projected_profit", -1).limit(limit)
        
        opportunities = await cursor.to_list(length=limit)
        
        # Get associated vehicles
        vehicle_ids = [opp["vehicle_id"] for opp in opportunities]
        vehicles_cursor = self.database.vehicles.find(
            {"_id": {"$in": vehicle_ids}}
        )
        vehicles = await vehicles_cursor.to_list(length=len(vehicle_ids))
        
        # Create a lookup dict
        vehicles_dict = {str(v["_id"]): v for v in vehicles}
        
        # Combine data
        results = []
        for opportunity in opportunities:
            vehicle = vehicles_dict.get(opportunity["vehicle_id"])
            if vehicle:
                results.append({
                    "opportunity": opportunity,
                    "vehicle": vehicle
                })
        
        return {
            "total_opportunities": len(results),
            "results": results,
            "search_id": search_id
        }
    
    async def close(self):
        """Close service connections"""
        await self.firecrawl.close()
        await self.perplexity.close()


# Helper function to create service instance
def get_search_engine() -> SearchEngine:
    """Get configured search engine instance"""
    return SearchEngine() 