"""
Firecrawl Service for Vehicle Data Collection

This service handles web scraping of vehicle listings from various marketplaces
using the Firecrawl API for robust and scalable data extraction.
"""

import asyncio
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass
from datetime import datetime
import re

from src.core.config import settings
from src.models.schemas import Vehicle, VehicleLocation, SearchCriteria


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    vehicles: List[Dict[str, Any]]
    source: str
    total_found: int
    success: bool
    error_message: Optional[str] = None
    raw_content: Optional[str] = None  # For debugging extraction issues


class FirecrawlService:
    """Service for scraping vehicle data using Firecrawl API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Marketplace configurations
        self.marketplaces = {
            "edmunds": {
                "base_url": "https://www.edmunds.com/inventory/srp.html",
                "search_patterns": {
                    "make": "make",
                    "model": "model", 
                    "year_min": "yearmin",
                    "year_max": "yearmax",
                    "price_min": "pricemin",
                    "price_max": "pricemax",
                    "location": "zip"
                }
            },
            "cars_com": {
                "base_url": "https://www.cars.com/shopping/results/",
                "search_patterns": {
                    "make": "make",
                    "model": "model",
                    "year_min": "year_min", 
                    "year_max": "year_max",
                    "price_min": "price_min",
                    "price_max": "price_max",
                    "location": "stock_type"
                }
            },
            "cargurus": {
                "base_url": "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action",
                "search_patterns": {
                    "make": "sourceContext",
                    "model": "modelFilters",
                    "year_min": "minYear",
                    "year_max": "maxYear", 
                    "price_min": "minPrice",
                    "price_max": "maxPrice",
                    "location": "distance"
                }
            }
        }
    
    async def search_marketplace(self, marketplace: str, criteria: SearchCriteria, location_zip: str = None) -> ScrapingResult:
        """
        Search a specific marketplace for vehicles matching criteria
        
        Args:
            marketplace: Name of marketplace to search ('autotrader', 'cars_com', 'cargurus')
            criteria: Search criteria object
            location_zip: ZIP code for location-based search
            
        Returns:
            ScrapingResult with found vehicles
        """
        try:
            if marketplace not in self.marketplaces:
                raise ValueError(f"Unsupported marketplace: {marketplace}")
            
            # Build search URL
            search_url = self._build_search_url(marketplace, criteria, location_zip)
            logger.info(f"🔥 FIRECRAWL: Searching {marketplace} with URL: {search_url}")
            
            # Use Firecrawl to scrape the search results
            logger.info(f"🔥 FIRECRAWL: Sending request to Firecrawl API for {marketplace}")
            scrape_result = await self._scrape_with_firecrawl(search_url, marketplace)
            logger.info(f"🔥 FIRECRAWL: API response - Success: {scrape_result['success']}")
            
            if not scrape_result["success"]:
                return ScrapingResult(
                    vehicles=[],
                    source=marketplace,
                    total_found=0,
                    success=False,
                    error_message=scrape_result.get("error")
                )
            
            # Extract vehicle data from scraped content
            content = scrape_result["data"]
            vehicles = self._extract_vehicles_from_content(content, marketplace)
            
            logger.info(f"Found {len(vehicles)} vehicles on {marketplace}")
            
            # Get content preview for debugging
            content_str = str(content)
            raw_preview = content_str[:2000] if content_str else None
            
            return ScrapingResult(
                vehicles=vehicles,
                source=marketplace,
                total_found=len(vehicles),
                success=True,
                raw_content=raw_preview
            )
            
        except Exception as e:
            logger.error(f"Error searching {marketplace}: {str(e)}")
            return ScrapingResult(
                vehicles=[],
                source=marketplace,
                total_found=0,
                success=False,
                error_message=str(e)
            )
    
    async def search_all_marketplaces(self, criteria: SearchCriteria, location_zips: List[str] = None) -> List[ScrapingResult]:
        """
        Search all configured marketplaces concurrently
        
        Args:
            criteria: Search criteria
            location_zips: List of ZIP codes to search (defaults to FL/GA major cities)
            
        Returns:
            List of ScrapingResult objects
        """
        if not location_zips:
            # Default FL/GA major city ZIP codes
            location_zips = [
                "33101",  # Miami, FL
                "32801",  # Orlando, FL  
                "33602",  # Tampa, FL
                "32301",  # Tallahassee, FL
                "30309",  # Atlanta, GA
                "31401",  # Savannah, GA
                "30901",  # Augusta, GA
                "31201"   # Macon, GA
            ]
        
        tasks = []
        for marketplace in self.marketplaces.keys():
            for zip_code in location_zips:
                task = self.search_marketplace(marketplace, criteria, zip_code)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, ScrapingResult):
                valid_results.append(result)
            else:
                logger.error(f"Task failed with exception: {result}")
        
        return valid_results
    
    def _build_search_url(self, marketplace: str, criteria: SearchCriteria, location_zip: str) -> str:
        """Build search URL for specific marketplace"""
        config = self.marketplaces[marketplace]
        base_url = config["base_url"]
        patterns = config["search_patterns"]
        
        params = []
        
        # Add make/model filters
        if criteria.makes:
            for make in criteria.makes:
                params.append(f"{patterns['make']}={make.lower()}")
        
        if criteria.models:
            for model in criteria.models:
                params.append(f"{patterns['model']}={model.lower()}")
        
        # Add year range
        if criteria.year_min:
            params.append(f"{patterns['year_min']}={criteria.year_min}")
        if criteria.year_max:
            params.append(f"{patterns['year_max']}={criteria.year_max}")
        
        # Add price range  
        if criteria.price_min:
            params.append(f"{patterns['price_min']}={int(criteria.price_min)}")
        if criteria.price_max:
            params.append(f"{patterns['price_max']}={int(criteria.price_max)}")
        
        # Add location
        if location_zip:
            params.append(f"{patterns['location']}={location_zip}")
        
        # Special handling per marketplace
        if marketplace == "edmunds":
            params.extend([
                "radius=100",
                "sort=price_asc"
            ])
        elif marketplace == "cars_com":
            params.extend([
                "maximum_distance=100",
                "stock_type=used"
            ])
        elif marketplace == "cargurus":
            params.extend([
                "distance=100",
                "inventorySearchWidgetType=AUTO"
            ])
        
        return f"{base_url}?{'&'.join(params)}"
    
    async def _scrape_with_firecrawl(self, url: str, marketplace: str) -> Dict[str, Any]:
        """Use Firecrawl API to scrape a URL"""
        try:
            payload = {
                "url": url,
                "formats": ["markdown", "html"],
                "onlyMainContent": True,
                "waitFor": 3000,  # Wait 3 seconds for dynamic content
                "actions": [
                    {
                        "type": "wait",
                        "milliseconds": 2000
                    },
                    {
                        "type": "scroll",
                        "direction": "down"
                    }
                ],
                "excludeTags": ["script", "style", "nav", "footer", "header"],
                "includeTags": ["div", "span", "a", "img", "p", "h1", "h2", "h3"]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"🔥 FIRECRAWL: Making API call to {self.base_url}/scrape")
            logger.info(f"🔥 FIRECRAWL: Payload URL: {url}")
            logger.info(f"🔥 FIRECRAWL: API key present: {bool(self.api_key)}")
            
            response = await self.client.post(
                f"{self.base_url}/scrape",
                json=payload,
                headers=headers
            )
            
            logger.info(f"🔥 FIRECRAWL: Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_length = len(str(data)) if data else 0
                logger.info(f"🔥 FIRECRAWL: Success! Content length: {content_length} chars")
                return {
                    "success": True,
                    "data": data
                }
            else:
                logger.error(f"🔥 FIRECRAWL: API error {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"🔥 FIRECRAWL: Exception during scraping: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_vehicles_from_content(self, scraped_data: Dict[str, Any], marketplace: str) -> List[Dict[str, Any]]:
        """Extract vehicle information from scraped content"""
        vehicles = []
        
        try:
            # Get the markdown content for easier parsing
            content = scraped_data.get("data", {}).get("markdown", "")
            if not content:
                content = scraped_data.get("data", {}).get("html", "")
            
            # Marketplace-specific extraction patterns
            if marketplace == "edmunds":
                vehicles = self._extract_edmunds_vehicles(content)
            elif marketplace == "cars_com":
                vehicles = self._extract_cars_com_vehicles(content)
            elif marketplace == "cargurus":
                vehicles = self._extract_cargurus_vehicles(content)
            
            logger.info(f"Extracted {len(vehicles)} vehicles from {marketplace}")
            
        except Exception as e:
            logger.error(f"Error extracting vehicles from {marketplace}: {str(e)}")
        
        return vehicles
    
    def _extract_edmunds_vehicles(self, content: str) -> List[Dict[str, Any]]:
        """Extract vehicle data from Edmunds content"""
        vehicles = []
        
        # Edmunds specific patterns
        price_pattern = r'\$([0-9,]+)'
        year_pattern = r'(20\d{2}|19\d{2})'
        mileage_pattern = r'([0-9,]+)\s*(?:mi|miles|MI|MILES)'
        
        # Split content into potential vehicle listings
        listings = content.split('\n\n')
        
        for listing in listings:
            if any(keyword in listing.lower() for keyword in ['$', 'mile', 'year', 'mpg']):
                try:
                    vehicle_data = self._parse_listing_text(listing, price_pattern, year_pattern, mileage_pattern)
                    if vehicle_data:
                        vehicle_data['source'] = 'edmunds'
                        vehicles.append(vehicle_data)
                except Exception as e:
                    logger.debug(f"Failed to parse Edmunds listing: {e}")
                    continue
        
        return vehicles
    
    def _extract_cars_com_vehicles(self, content: str) -> List[Dict[str, Any]]:
        """Extract vehicle data from Cars.com content"""
        vehicles = []
        
        # Cars.com specific patterns
        price_pattern = r'\$([0-9,]+)'
        year_pattern = r'(20\d{2}|19\d{2})'
        mileage_pattern = r'([0-9,]+)\s*(?:mi|miles|MI|MILES)'
        
        listings = content.split('\n\n')
        
        for listing in listings:
            if any(keyword in listing.lower() for keyword in ['$', 'mile', 'year', 'mpg']):
                try:
                    vehicle_data = self._parse_listing_text(listing, price_pattern, year_pattern, mileage_pattern)
                    if vehicle_data:
                        vehicle_data['source'] = 'cars.com'
                        vehicles.append(vehicle_data)
                except Exception as e:
                    logger.debug(f"Failed to parse Cars.com listing: {e}")
                    continue
        
        return vehicles
    
    def _extract_cargurus_vehicles(self, content: str) -> List[Dict[str, Any]]:
        """Extract vehicle data from CarGurus content"""
        vehicles = []
        
        # CarGurus specific patterns
        price_pattern = r'\$([0-9,]+)'
        year_pattern = r'(20\d{2}|19\d{2})'
        mileage_pattern = r'([0-9,]+)\s*(?:mi|miles|MI|MILES)'
        
        listings = content.split('\n\n')
        
        for listing in listings:
            if any(keyword in listing.lower() for keyword in ['$', 'mile', 'year', 'mpg']):
                try:
                    vehicle_data = self._parse_listing_text(listing, price_pattern, year_pattern, mileage_pattern)
                    if vehicle_data:
                        vehicle_data['source'] = 'cargurus'
                        vehicles.append(vehicle_data)
                except Exception as e:
                    logger.debug(f"Failed to parse CarGurus listing: {e}")
                    continue
        
        return vehicles
    
    def _parse_listing_text(self, text: str, price_pattern: str, year_pattern: str, mileage_pattern: str) -> Optional[Dict[str, Any]]:
        """Parse a single listing text and extract vehicle data"""
        try:
            # Extract price
            price_match = re.search(price_pattern, text)
            price = None
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
            
            # Extract year
            year_match = re.search(year_pattern, text)
            year = None
            if year_match:
                year = int(year_match.group(1))
            
            # Extract mileage
            mileage_match = re.search(mileage_pattern, text)
            mileage = None
            if mileage_match:
                mileage = int(mileage_match.group(1).replace(',', ''))
            
            # Extract make/model (basic pattern matching)
            make, model = self._extract_make_model(text)
            
            # Extract location
            location = self._extract_location(text)
            
            # Only return if we have essential data
            if price and year and make:
                return {
                    'price': price,
                    'year': year,
                    'make': make,
                    'model': model or 'Unknown',
                    'mileage': mileage or 0,
                    'location': location,
                    'url': '',  # We'll need to extract this from the HTML
                    'external_id': f"{make}_{model}_{year}_{price}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'last_seen_at': datetime.utcnow(),
                    'discovered_at': datetime.utcnow(),
                    'is_active': True,
                    'images': [],
                    'features': []
                }
                
        except Exception as e:
            logger.debug(f"Error parsing listing: {e}")
        
        return None
    
    def _extract_make_model(self, text: str) -> tuple:
        """Extract make and model from text using common patterns"""
        # Common car makes
        makes = [
            'toyota', 'honda', 'ford', 'chevrolet', 'chevy', 'nissan', 'hyundai',
            'kia', 'bmw', 'mercedes', 'audi', 'volkswagen', 'vw', 'mazda', 'subaru',
            'lexus', 'acura', 'infiniti', 'volvo', 'jeep', 'dodge', 'chrysler',
            'cadillac', 'buick', 'gmc', 'lincoln', 'mitsubishi', 'isuzu'
        ]
        
        text_lower = text.lower()
        make = None
        model = None
        
        for make_name in makes:
            if make_name in text_lower:
                make = make_name.title()
                # Try to find model after make
                pattern = rf'{make_name}\s+(\w+)'
                match = re.search(pattern, text_lower)
                if match:
                    model = match.group(1).title()
                break
        
        return make, model
    
    def _extract_location(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract location information from text"""
        # Pattern for city, state
        location_pattern = r'([A-Za-z\s]+),\s*([A-Z]{2})'
        match = re.search(location_pattern, text)
        
        if match:
            city = match.group(1).strip()
            state = match.group(2).strip()
            return {
                'city': city,
                'state': state,
                'coordinates': []  # We'd need geocoding for this
            }
        
        return None
    
    async def batch_scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Batch scrape multiple vehicle detail URLs
        
        Args:
            urls: List of vehicle detail page URLs
            
        Returns:
            List of detailed vehicle data
        """
        tasks = []
        for url in urls[:10]:  # Limit to 10 concurrent requests
            task = self._scrape_vehicle_details(url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get('success'):
                valid_results.append(result['data'])
        
        return valid_results
    
    async def _scrape_vehicle_details(self, url: str) -> Dict[str, Any]:
        """Scrape detailed information from a vehicle listing page"""
        try:
            payload = {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "waitFor": 2000,
                "excludeTags": ["script", "style", "nav", "footer"]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.base_url}/scrape",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": self._parse_vehicle_details(data.get("data", {}))
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error scraping vehicle details from {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_vehicle_details(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detailed vehicle information from scraped content"""
        content = scraped_data.get("markdown", "")
        
        # Extract additional details like VIN, features, condition, etc.
        details = {
            'vin': self._extract_vin(content),
            'features': self._extract_features(content),
            'condition': self._extract_condition(content),
            'images': self._extract_images(content)
        }
        
        return details
    
    def _extract_vin(self, content: str) -> Optional[str]:
        """Extract VIN from content"""
        vin_pattern = r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})'
        match = re.search(vin_pattern, content, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_features(self, content: str) -> List[str]:
        """Extract vehicle features from content"""
        features = []
        feature_keywords = [
            'leather', 'sunroof', 'navigation', 'bluetooth', 'backup camera',
            'heated seats', 'air conditioning', 'cruise control', 'alloy wheels',
            'automatic', 'manual', 'awd', '4wd', 'fwd'
        ]
        
        content_lower = content.lower()
        for keyword in feature_keywords:
            if keyword in content_lower:
                features.append(keyword.title())
        
        return features
    
    def _extract_condition(self, content: str) -> str:
        """Extract vehicle condition from content"""
        conditions = ['excellent', 'very good', 'good', 'fair', 'poor', 'new', 'used', 'certified']
        content_lower = content.lower()
        
        for condition in conditions:
            if condition in content_lower:
                return condition.title()
        
        return 'Used'  # Default
    
    def _extract_images(self, content: str) -> List[str]:
        """Extract image URLs from content"""
        # This would need to parse the HTML data for img tags
        # For now, return empty list
        return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Helper function to create service instance
def get_firecrawl_service() -> FirecrawlService:
    """Get configured Firecrawl service instance"""
    return FirecrawlService() 