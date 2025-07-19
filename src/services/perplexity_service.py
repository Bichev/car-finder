"""
Perplexity AI Service for Market Analysis

This service provides AI-powered market research, pricing analysis, and 
vehicle valuation insights using the Perplexity API.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from loguru import logger
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.core.config import settings
from src.models.schemas import Vehicle, MarketAnalysis


@dataclass
class MarketInsight:
    """Market analysis insight from Perplexity"""
    vehicle_info: str
    market_value_range: Optional[Dict[str, float]]
    market_conditions: str
    regional_factors: List[str]
    confidence_score: float
    sources: List[str]
    analysis_date: datetime


@dataclass
class CompetitiveAnalysis:
    """Competitive pricing analysis"""
    average_market_price: float
    price_range: Dict[str, float]  # {"min": x, "max": y}
    comparable_listings: List[Dict[str, Any]]
    market_trend: str  # "rising", "falling", "stable"
    days_on_market_avg: Optional[int]


class PerplexityService:
    """Service for AI-powered market analysis using Perplexity API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.client = httpx.AsyncClient(timeout=30.0)  # Reduced from 120s for better UX
        
        # Model configuration
        self.model = "sonar-pro"  # Advanced search model with enhanced citations
        self.max_tokens = 4000
        
        # Cache for recent queries to avoid duplicate API calls
        self._cache = {}
        self._cache_duration = timedelta(hours=6)  # Cache for 6 hours
    
    async def analyze_vehicle_market(self, vehicle: Vehicle, location_state: str = None) -> MarketInsight:
        """
        Get comprehensive market analysis for a specific vehicle
        
        Args:
            vehicle: Vehicle object to analyze
            location_state: State for regional analysis (FL, GA, etc.)
            
        Returns:
            MarketInsight with detailed analysis
        """
        try:
            # Build analysis query
            location_filter = f" in {location_state}" if location_state else " in Florida and Georgia"
            
            query = f"""
            Analyze the current used car market for a {vehicle.year} {vehicle.make} {vehicle.model} with {vehicle.mileage:,} miles{location_filter}.
            
            Please provide:
            1. Current market value range (low, average, high)
            2. Market conditions and trends for this vehicle
            3. Regional factors affecting pricing in the Southeast US
            4. Factors that could affect resale value
            5. Comparable recent sales data if available
            
            Focus on actual market data and recent sales, not just book values.
            """
            
            # Check cache first
            cache_key = f"market_analysis_{vehicle.make}_{vehicle.model}_{vehicle.year}_{vehicle.mileage//1000}k_{location_state}"
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                logger.info(f"Using cached market analysis for {vehicle.year} {vehicle.make} {vehicle.model}")
                return cached_result
            
            # Get AI analysis
            response = await self._query_perplexity(query)
            
            if not response["success"]:
                raise Exception(f"Perplexity API error: {response['error']}")
            
            # Parse the response
            insight = self._parse_market_analysis(response["data"], vehicle, location_state)
            
            # Cache the result
            self._cache_result(cache_key, insight)
            
            logger.info(f"Generated market analysis for {vehicle.year} {vehicle.make} {vehicle.model}")
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing vehicle market: {str(e)}")
            # Return a basic insight with error indication
            return MarketInsight(
                vehicle_info=f"{vehicle.year} {vehicle.make} {vehicle.model}",
                market_value_range=None,
                market_conditions=f"Analysis unavailable: {str(e)}",
                regional_factors=[],
                confidence_score=0.0,
                sources=[],
                analysis_date=datetime.utcnow()
            )
    
    async def get_competitive_pricing(self, vehicle: Vehicle, radius_miles: int = 100) -> CompetitiveAnalysis:
        """
        Get competitive pricing analysis for similar vehicles
        
        Args:
            vehicle: Vehicle to analyze
            radius_miles: Search radius for comparables
            
        Returns:
            CompetitiveAnalysis with pricing insights
        """
        try:
            query = f"""
            Find current market pricing for used {vehicle.year} {vehicle.make} {vehicle.model} vehicles 
            with approximately {vehicle.mileage:,} miles within {radius_miles} miles of Florida and Georgia.
            
            Please provide:
            1. Average selling price in the region
            2. Price range (lowest to highest for similar vehicles)
            3. How long similar vehicles typically stay on the market
            4. Current market trend (increasing, decreasing, or stable prices)
            5. Any recent comparable sales data
            
            Focus on actual listing prices and recent sales, not just estimated values.
            """
            
            # Check cache
            cache_key = f"competitive_pricing_{vehicle.make}_{vehicle.model}_{vehicle.year}_{vehicle.mileage//1000}k"
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
            
            response = await self._query_perplexity(query)
            
            if not response["success"]:
                raise Exception(f"Perplexity API error: {response['error']}")
            
            analysis = self._parse_competitive_analysis(response["data"], vehicle)
            
            # Cache result
            self._cache_result(cache_key, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting competitive pricing: {str(e)}")
            return CompetitiveAnalysis(
                average_market_price=vehicle.price,  # Fallback to listed price
                price_range={"min": vehicle.price * 0.9, "max": vehicle.price * 1.1},
                comparable_listings=[],
                market_trend="unknown",
                days_on_market_avg=None
            )
    
    async def analyze_resale_potential(self, vehicle: Vehicle, target_market: str = "Southeast") -> Dict[str, Any]:
        """
        Analyze resale potential and factors affecting future value
        
        Args:
            vehicle: Vehicle to analyze
            target_market: Target resale market
            
        Returns:
            Dictionary with resale analysis
        """
        try:
            query = f"""
            Analyze the resale potential for a {vehicle.year} {vehicle.make} {vehicle.model} 
            with {vehicle.mileage:,} miles in the {target_market} market.
            
            Consider:
            1. Depreciation patterns for this make/model
            2. Reliability and maintenance costs
            3. Market demand trends
            4. Seasonal factors affecting sales
            5. Regional preferences in the Southeast
            6. Expected resale timeline (30-90 days)
            
            Provide insights on optimal resale timing and pricing strategy.
            """
            
            response = await self._query_perplexity(query)
            
            if not response["success"]:
                raise Exception(f"Perplexity API error: {response['error']}")
            
            return self._parse_resale_analysis(response["data"])
            
        except Exception as e:
            logger.error(f"Error analyzing resale potential: {str(e)}")
            return {
                "resale_score": 0.5,
                "factors": [f"Analysis unavailable: {str(e)}"],
                "optimal_timing": "unknown",
                "pricing_strategy": "market_rate"
            }
    
    async def research_market_trends(self, make: str, model: str = None, timeframe: str = "6 months") -> Dict[str, Any]:
        """
        Research broader market trends for specific makes/models
        
        Args:
            make: Vehicle make
            model: Vehicle model (optional)
            timeframe: Analysis timeframe
            
        Returns:
            Market trends analysis
        """
        try:
            model_filter = f" {model}" if model else ""
            query = f"""
            Research current market trends for {make}{model_filter} vehicles over the past {timeframe}.
            
            Include:
            1. Price trend direction (up, down, stable)
            2. Inventory levels and supply/demand
            3. Consumer preference shifts
            4. Economic factors affecting this segment
            5. Regional variations in the Southeast US
            6. Seasonal patterns
            
            Focus on data that would help with buying and reselling decisions.
            """
            
            cache_key = f"market_trends_{make}_{model or 'all'}_{timeframe}"
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
            
            response = await self._query_perplexity(query)
            
            if not response["success"]:
                raise Exception(f"Perplexity API error: {response['error']}")
            
            trends = self._parse_market_trends(response["data"])
            
            # Cache for longer since trends change slowly
            self._cache_result(cache_key, trends, duration=timedelta(hours=12))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error researching market trends: {str(e)}")
            return {
                "trend_direction": "unknown",
                "confidence": 0.0,
                "factors": [f"Analysis unavailable: {str(e)}"]
            }
    
    async def _query_perplexity(self, query: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Send a query to Perplexity API
        
        Args:
            query: The research query
            system_prompt: Optional system prompt
            
        Returns:
            API response
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                messages.append({
                    "role": "system", 
                    "content": """You are an expert automotive market analyst specializing in used car 
                    valuation and market trends. Provide accurate, data-driven insights based on current 
                    market conditions. Focus on actionable information for car dealers and investors."""
                })
            
            messages.append({
                "role": "user",
                "content": query
            })
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": 0.2,  # Lower temperature for more factual responses
                "top_p": 0.9,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data
                }
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error querying Perplexity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_market_analysis(self, api_response: Dict[str, Any], vehicle: Vehicle, location: str) -> MarketInsight:
        """Parse market analysis from API response"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            
            # Extract market value range using regex
            value_range = self._extract_price_range(content)
            
            # Extract market conditions
            conditions = self._extract_market_conditions(content)
            
            # Extract regional factors
            regional_factors = self._extract_regional_factors(content)
            
            # Calculate confidence based on specificity of response
            confidence = self._calculate_confidence(content)
            
            # Extract sources (if available)
            sources = self._extract_sources(content)
            
            return MarketInsight(
                vehicle_info=f"{vehicle.year} {vehicle.make} {vehicle.model}",
                market_value_range=value_range,
                market_conditions=conditions,
                regional_factors=regional_factors,
                confidence_score=confidence,
                sources=sources,
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error parsing market analysis: {str(e)}")
            return MarketInsight(
                vehicle_info=f"{vehicle.year} {vehicle.make} {vehicle.model}",
                market_value_range=None,
                market_conditions="Analysis parsing failed",
                regional_factors=[],
                confidence_score=0.0,
                sources=[],
                analysis_date=datetime.utcnow()
            )
    
    def _parse_competitive_analysis(self, api_response: Dict[str, Any], vehicle: Vehicle) -> CompetitiveAnalysis:
        """Parse competitive analysis from API response"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            
            # Extract average price
            avg_price = self._extract_average_price(content) or vehicle.price
            
            # Extract price range
            price_range = self._extract_price_range(content) or {
                "min": avg_price * 0.85,
                "max": avg_price * 1.15
            }
            
            # Extract market trend
            trend = self._extract_market_trend(content)
            
            # Extract days on market
            days_on_market = self._extract_days_on_market(content)
            
            return CompetitiveAnalysis(
                average_market_price=avg_price,
                price_range=price_range,
                comparable_listings=[],  # Would need additional API calls to get specific listings
                market_trend=trend,
                days_on_market_avg=days_on_market
            )
            
        except Exception as e:
            logger.error(f"Error parsing competitive analysis: {str(e)}")
            return CompetitiveAnalysis(
                average_market_price=vehicle.price,
                price_range={"min": vehicle.price * 0.9, "max": vehicle.price * 1.1},
                comparable_listings=[],
                market_trend="unknown",
                days_on_market_avg=None
            )
    
    def _parse_resale_analysis(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resale potential analysis"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            
            return {
                "resale_score": self._extract_resale_score(content),
                "factors": self._extract_resale_factors(content),
                "optimal_timing": self._extract_optimal_timing(content),
                "pricing_strategy": self._extract_pricing_strategy(content),
                "analysis_text": content
            }
            
        except Exception as e:
            logger.error(f"Error parsing resale analysis: {str(e)}")
            return {
                "resale_score": 0.5,
                "factors": ["Analysis parsing failed"],
                "optimal_timing": "unknown",
                "pricing_strategy": "market_rate"
            }
    
    def _parse_market_trends(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse market trends analysis"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            
            return {
                "trend_direction": self._extract_trend_direction(content),
                "confidence": self._calculate_confidence(content),
                "factors": self._extract_trend_factors(content),
                "seasonal_patterns": self._extract_seasonal_patterns(content),
                "analysis_text": content
            }
            
        except Exception as e:
            logger.error(f"Error parsing market trends: {str(e)}")
            return {
                "trend_direction": "unknown",
                "confidence": 0.0,
                "factors": ["Analysis parsing failed"]
            }
    
    def _extract_price_range(self, content: str) -> Optional[Dict[str, float]]:
        """Extract price range from analysis text"""
        import re
        
        # Look for patterns like "$15,000 - $18,000" or "15k to 18k"
        price_patterns = [
            r'\$([0-9,]+)\s*(?:-|to)\s*\$([0-9,]+)',
            r'([0-9]+)k\s*(?:-|to)\s*([0-9]+)k',
            r'low:\s*\$([0-9,]+).*high:\s*\$([0-9,]+)',
            r'range.*\$([0-9,]+).*\$([0-9,]+)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    match = matches[0]
                    if 'k' in pattern:
                        min_price = float(match[0]) * 1000
                        max_price = float(match[1]) * 1000
                    else:
                        min_price = float(match[0].replace(',', ''))
                        max_price = float(match[1].replace(',', ''))
                    
                    # Calculate average
                    avg_price = (min_price + max_price) / 2
                    
                    return {
                        "min": min_price,
                        "max": max_price,
                        "average": avg_price
                    }
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_average_price(self, content: str) -> Optional[float]:
        """Extract average market price from text"""
        import re
        
        avg_patterns = [
            r'average.*\$([0-9,]+)',
            r'typical.*\$([0-9,]+)',
            r'median.*\$([0-9,]+)'
        ]
        
        for pattern in avg_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        
        return None
    
    def _extract_market_conditions(self, content: str) -> str:
        """Extract market conditions summary"""
        # Look for key phrases about market conditions
        conditions_indicators = [
            "market conditions", "current market", "market situation", 
            "demand", "supply", "pricing trends"
        ]
        
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in conditions_indicators):
                relevant_sentences.append(sentence.strip())
        
        return '. '.join(relevant_sentences[:3]) if relevant_sentences else "Market conditions not specified"
    
    def _extract_regional_factors(self, content: str) -> List[str]:
        """Extract regional factors affecting pricing"""
        factors = []
        regional_keywords = [
            "florida", "georgia", "southeast", "regional", "local", 
            "weather", "climate", "hurricane", "seasonal"
        ]
        
        sentences = content.lower().split('.')
        for sentence in sentences:
            if any(keyword in sentence for keyword in regional_keywords):
                factors.append(sentence.strip().capitalize())
        
        return factors[:5]  # Limit to top 5 factors
    
    def _extract_market_trend(self, content: str) -> str:
        """Extract market trend direction"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["increasing", "rising", "upward", "growth"]):
            return "rising"
        elif any(word in content_lower for word in ["decreasing", "falling", "declining", "down"]):
            return "falling"
        elif any(word in content_lower for word in ["stable", "steady", "consistent", "flat"]):
            return "stable"
        else:
            return "unknown"
    
    def _extract_days_on_market(self, content: str) -> Optional[int]:
        """Extract average days on market"""
        import re
        
        patterns = [
            r'([0-9]+)\s*days?\s*on\s*market',
            r'sell.*([0-9]+)\s*days?',
            r'([0-9]+)\s*days?.*sell'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _extract_sources(self, content: str) -> List[str]:
        """Extract sources mentioned in the analysis"""
        sources = []
        source_patterns = [
            r'(AutoTrader|Cars\.com|CarGurus|KBB|Kelley Blue Book|Edmunds|NADA)',
            r'according to ([^,\.]+)',
            r'source: ([^,\.]+)'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            sources.extend(matches)
        
        return list(set(sources))[:5]  # Remove duplicates and limit
    
    def _calculate_confidence(self, content: str) -> float:
        """Calculate confidence score based on content specificity"""
        confidence_indicators = [
            "according to", "data shows", "recent sales", "market data",
            "statistics", "analysis", "research", "$"
        ]
        
        score = 0.0
        content_lower = content.lower()
        
        for indicator in confidence_indicators:
            if indicator in content_lower:
                score += 0.1
        
        # Bonus for specific numbers
        import re
        if re.search(r'\$[0-9,]+', content):
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_resale_score(self, content: str) -> float:
        """Extract or calculate resale potential score"""
        # Look for explicit scores or ratings
        import re
        
        score_patterns = [
            r'score.*([0-9]\.?[0-9]*)',
            r'rating.*([0-9]\.?[0-9]*)',
            r'([0-9])/10',
            r'([0-9])\.?[0-9]*/5'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    return min(score / 10.0, 1.0) if score > 1.0 else score
                except ValueError:
                    continue
        
        # If no explicit score, infer from positive/negative language
        positive_words = ["excellent", "good", "strong", "high", "favorable"]
        negative_words = ["poor", "weak", "low", "unfavorable", "difficult"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 0.7
        elif negative_count > positive_count:
            return 0.3
        else:
            return 0.5
    
    def _extract_resale_factors(self, content: str) -> List[str]:
        """Extract factors affecting resale"""
        sentences = content.split('.')
        factors = []
        
        factor_keywords = [
            "reliability", "maintenance", "depreciation", "demand", 
            "reputation", "fuel economy", "features", "condition"
        ]
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in factor_keywords):
                factors.append(sentence.strip())
        
        return factors[:5]
    
    def _extract_optimal_timing(self, content: str) -> str:
        """Extract optimal resale timing"""
        timing_patterns = [
            r'(spring|summer|fall|winter)',
            r'([0-9]+)\s*(?:days?|weeks?|months?)',
            r'(immediately|quickly|soon|later)'
        ]
        
        for pattern in timing_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "30-60 days"  # Default
    
    def _extract_pricing_strategy(self, content: str) -> str:
        """Extract recommended pricing strategy"""
        content_lower = content.lower()
        
        if "competitive" in content_lower or "below market" in content_lower:
            return "competitive"
        elif "premium" in content_lower or "above market" in content_lower:
            return "premium"
        elif "market rate" in content_lower or "fair market" in content_lower:
            return "market_rate"
        else:
            return "market_rate"
    
    def _extract_trend_direction(self, content: str) -> str:
        """Extract overall trend direction"""
        return self._extract_market_trend(content)
    
    def _extract_trend_factors(self, content: str) -> List[str]:
        """Extract factors influencing trends"""
        return self._extract_regional_factors(content)
    
    def _extract_seasonal_patterns(self, content: str) -> List[str]:
        """Extract seasonal patterns"""
        seasons = ["spring", "summer", "fall", "winter"]
        patterns = []
        
        for season in seasons:
            if season in content.lower():
                # Find the sentence containing the season
                sentences = content.split('.')
                for sentence in sentences:
                    if season in sentence.lower():
                        patterns.append(f"{season.capitalize()}: {sentence.strip()}")
                        break
        
        return patterns
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result if still valid"""
        if key in self._cache:
            cached_data, timestamp = self._cache[key]
            if datetime.utcnow() - timestamp < self._cache_duration:
                return cached_data
            else:
                # Remove expired cache entry
                del self._cache[key]
        return None
    
    def _cache_result(self, key: str, data: Any, duration: timedelta = None) -> None:
        """Cache result with timestamp"""
        self._cache[key] = (data, datetime.utcnow())
        
        # Clean old cache entries periodically
        if len(self._cache) > 100:
            cutoff = datetime.utcnow() - (duration or self._cache_duration)
            expired_keys = [
                k for k, (_, timestamp) in self._cache.items()
                if timestamp < cutoff
            ]
            for k in expired_keys:
                del self._cache[k]
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Helper function to create service instance
def get_perplexity_service() -> PerplexityService:
    """Get configured Perplexity service instance"""
    return PerplexityService() 