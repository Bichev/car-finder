"""
Playwright Web Scraping Service

This service provides robust web scraping for car marketplaces using Playwright
for reliable automation, form interaction, and data extraction.
"""

import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from dataclasses import dataclass
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from src.core.config import settings
from src.models.schemas import SearchCriteria
from src.services.firecrawl_service import ScrapingResult  # Reuse the same result format


@dataclass
class PlaywrightConfig:
    """Configuration for Playwright scraping"""
    headless: bool = True
    timeout: int = 30000  # 30 seconds
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    viewport_width: int = 1920
    viewport_height: int = 1080


class PlaywrightScrapingService:
    """Service for scraping vehicle data using Playwright automation"""
    
    def __init__(self, config: PlaywrightConfig = None):
        self.config = config or PlaywrightConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # Marketplace configurations
        self.marketplaces = {
            "cars_com": {
                "name": "Cars.com",
                "url": "https://www.cars.com/shopping/",
                "supports_automation": True
            },
            "edmunds": {
                "name": "Edmunds",
                "url": "https://www.edmunds.com/inventory/",
                "supports_automation": True
            },
            "cargurus": {
                "name": "CarGurus", 
                "url": "https://www.cargurus.com/Cars/",
                "supports_automation": True
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize Playwright browser and context"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with optimized settings
            # Note: Will try to use downloaded browsers, fallback to error with helpful message
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create browser context with realistic settings
            self.context = await self.browser.new_context(
                user_agent=self.config.user_agent,
                viewport={
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br'
                }
            )
            
            logger.info("🎭 Playwright browser initialized successfully")
            
        except Exception as e:
            logger.error(f"🎭 Failed to initialize Playwright: {str(e)}")
            raise
    
    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("🎭 Playwright resources cleaned up")
        except Exception as e:
            logger.error(f"🎭 Error closing Playwright: {str(e)}")
    
    async def search_marketplace(self, marketplace: str, criteria: SearchCriteria, location_zip: str = "33101") -> ScrapingResult:
        """
        Search a specific marketplace using Playwright automation
        
        Args:
            marketplace: Name of marketplace ('cars_com', 'edmunds', 'cargurus')
            criteria: Search criteria with make, model, year, price filters
            location_zip: ZIP code for location-based search
            
        Returns:
            ScrapingResult with vehicles found and metadata
        """
        try:
            if marketplace not in self.marketplaces:
                raise ValueError(f"Unsupported marketplace: {marketplace}")
            
            logger.info(f"🎭 Starting Playwright search on {marketplace}")
            
            # Create new page for this search
            page = await self.context.new_page()
            
            try:
                # Set page timeout
                page.set_default_timeout(self.config.timeout)
                
                # Route to marketplace-specific scraper
                if marketplace == "cars_com":
                    vehicles = await self._scrape_cars_com(page, criteria, location_zip)
                elif marketplace == "edmunds":
                    vehicles = await self._scrape_edmunds(page, criteria, location_zip)
                elif marketplace == "cargurus":
                    vehicles = await self._scrape_cargurus(page, criteria, location_zip)
                else:
                    vehicles = []
                
                logger.info(f"🎭 Found {len(vehicles)} vehicles on {marketplace}")
                
                return ScrapingResult(
                    vehicles=vehicles,
                    source=marketplace,
                    total_found=len(vehicles),
                    success=True,
                    raw_content=f"Playwright automation results from {marketplace}"
                )
                
            finally:
                await page.close()
                
        except Exception as e:
            logger.error(f"🎭 Error searching {marketplace}: {str(e)}")
            return ScrapingResult(
                vehicles=[],
                source=marketplace,
                total_found=0,
                success=False,
                error_message=str(e),
                raw_content=f"Error during Playwright automation: {str(e)}"
            )
    
    async def _scrape_cars_com(self, page: Page, criteria: SearchCriteria, location_zip: str) -> List[Dict[str, Any]]:
        """Scrape Cars.com using form automation"""
        try:
            logger.info("🎭 Navigating to Cars.com...")
            await page.goto("https://www.cars.com/shopping/", wait_until="domcontentloaded")
            
            # Wait a bit for JS to fully load
            await page.wait_for_timeout(5000)
            logger.info("🎭 Page loaded, looking for search elements...")
            
            # Take a screenshot for debugging and log page info
            current_url = page.url
            page_title = await page.title()
            logger.info(f"🎭 Current URL: {current_url}")
            logger.info(f"🎭 Page title: {page_title}")
            
            # Debug: log all input elements on the page
            all_inputs = await page.locator('input').all()
            logger.info(f"🎭 Found {len(all_inputs)} total input elements")
            
            for i, inp in enumerate(all_inputs[:10]):  # Log first 10 inputs
                try:
                    placeholder = await inp.get_attribute('placeholder') or "no placeholder"
                    input_type = await inp.get_attribute('type') or "no type"
                    input_name = await inp.get_attribute('name') or "no name"
                    is_visible = await inp.is_visible()
                    logger.info(f"🎭 Input {i+1}: type='{input_type}', name='{input_name}', placeholder='{placeholder}', visible={is_visible}")
                except:
                    logger.info(f"🎭 Input {i+1}: could not read attributes")
            
            # Also check for any obvious search-related text on page
            search_texts = ['Search', 'Make', 'Model', 'Year', 'Price', 'Location']
            for text in search_texts:
                try:
                    elements = await page.locator(f':has-text("{text}")').count()
                    if elements > 0:
                        logger.info(f"🎭 Found {elements} elements containing '{text}'")
                except:
                    pass
            
            # Look for different types of search interfaces
            search_found = False
            
            # Try the main search form first with updated selectors
            main_search_selectors = [
                'input[name="one_hitter"]',  # Cars.com main search field (PRIORITY)
                'input[data-testid="sitewide-search-filter-text"]',
                'input[name="searchTerm"]', 
                'input[placeholder*="make"]',
                'input[placeholder*="Make"]',
                'input[placeholder*="Search"]',
                'input[placeholder*="Enter"]',
                '.search-input',
                '#search-input',
                '[data-qa="search-input"]',
                'input[type="search"]',
                'input[aria-label*="search"]',
                'input[aria-label*="Search"]',
                # Modern Cars.com specific selectors
                'input[data-linkname*="search"]',
                'input[class*="search"]',
                'input[id*="search"]'
            ]
            
            for selector in main_search_selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        logger.info(f"🎭 Found search input: {selector}")
                        search_found = True
                        break
                except:
                    continue
            
            if not search_found:
                logger.warning("🎭 Main search not found, trying alternative approach...")
                # Try to find any input field and use it
                all_inputs = await page.locator('input[type="text"], input[type="search"], input:not([type])').all()
                logger.info(f"🎭 Found {len(all_inputs)} input fields on page")
                
                if len(all_inputs) > 0:
                    # Use the first visible input
                    for inp in all_inputs:
                        if await inp.is_visible():
                            search_found = True
                            logger.info("🎭 Using first visible input field")
                            break
            
            if not search_found:
                logger.warning("🎭 No search inputs found on main page, trying advanced search page...")
                
                # Try navigating to the advanced search page
                try:
                    await page.goto("https://www.cars.com/shopping/results/", wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)
                    
                    # Look for search elements on results page
                    results_search_selectors = [
                        'input[placeholder*="Make"]',
                        'input[placeholder*="Model"]',
                        'input[name="make"]',
                        'input[name="model"]',
                        'select[name="make"]',
                        'select[name="model"]'
                    ]
                    
                    for selector in results_search_selectors:
                        try:
                            element = page.locator(selector)
                            if await element.count() > 0:
                                logger.info(f"🎭 Found search element on results page: {selector}")
                                search_found = True
                                break
                        except:
                            continue
                    
                    if not search_found:
                        logger.error("🎭 No search forms found on advanced search page either")
                        return []
                        
                except Exception as e:
                    logger.error(f"🎭 Failed to navigate to advanced search: {str(e)}")
                    return []
            
            # Wait for any search interface to be ready
            await page.wait_for_timeout(2000)
            
            # Fill search form
            if criteria.makes and criteria.models:
                make = criteria.makes[0]
                model = criteria.models[0]
                search_query = f"{make} {model}"
                logger.info(f"🎭 Searching for: {search_query} in {location_zip}")
                
                # Try using separate Make/Model dropdowns first (modern Cars.com)
                make_filled = False
                model_filled = False
                
                # Try make dropdown/input
                make_selectors = [
                    'select[name="make"]',
                    'input[name="make"]',
                    'select[placeholder*="Make"]',
                    'input[placeholder*="Make"]',
                    'select[data-qa*="make"]',
                    'input[data-qa*="make"]',
                    # Cars.com specific
                    'input[name="one_hitter"]'  # Main search field on Cars.com
                ]
                
                for selector in make_selectors:
                    try:
                        make_element = page.locator(selector)
                        if await make_element.count() > 0 and await make_element.is_visible():
                            if 'select' in selector:
                                # Handle dropdown
                                await make_element.select_option(label=make)
                                logger.info(f"🎭 Selected make '{make}' from dropdown: {selector}")
                            else:
                                # Handle text input
                                await make_element.clear()
                                await make_element.fill(make)
                                logger.info(f"🎭 Filled make '{make}' in input: {selector}")
                            make_filled = True
                            break
                    except Exception as e:
                        logger.debug(f"🎭 Failed to fill make with {selector}: {str(e)}")
                        continue
                
                # Try model dropdown/input
                model_selectors = [
                    'select[name="model"]',
                    'input[name="model"]',
                    'select[placeholder*="Model"]',
                    'input[placeholder*="Model"]',
                    'select[data-qa*="model"]',
                    'input[data-qa*="model"]'
                ]
                
                for selector in model_selectors:
                    try:
                        model_element = page.locator(selector)
                        if await model_element.count() > 0 and await model_element.is_visible():
                            if 'select' in selector:
                                # Handle dropdown
                                await model_element.select_option(label=model)
                                logger.info(f"🎭 Selected model '{model}' from dropdown: {selector}")
                            else:
                                # Handle text input
                                await model_element.clear()
                                await model_element.fill(model)
                                logger.info(f"🎭 Filled model '{model}' in input: {selector}")
                            model_filled = True
                            break
                    except Exception as e:
                        logger.debug(f"🎭 Failed to fill model with {selector}: {str(e)}")
                        continue
                
                # If separate fields didn't work, try single search field
                filled = make_filled or model_filled
                if not filled:
                    logger.info("🎭 Trying single search field approach...")
                    search_selectors = [
                        'input[name="one_hitter"]',  # Cars.com main search field (PRIORITY)
                        'input[data-testid="sitewide-search-filter-text"]',
                        'input[name="searchTerm"]',
                        'input[placeholder*="make"]',
                        'input[placeholder*="Make"]',
                        'input[placeholder*="Search"]',
                        '.search-input',
                        '#search-input'
                    ]
                    
                    for selector in search_selectors:
                        try:
                            search_input = page.locator(selector)
                            if await search_input.count() > 0 and await search_input.is_visible():
                                logger.info(f"🎭 Filling search input with: {search_query}")
                                await search_input.clear()
                                await search_input.fill(search_query)
                                filled = True
                                logger.info(f"🎭 Successfully filled search input: {selector}")
                                break
                        except Exception as e:
                            logger.debug(f"🎭 Failed to fill {selector}: {str(e)}")
                            continue
                
                if not filled:
                    logger.warning("🎭 Could not find search input, trying alternative methods...")
                    # Try clicking somewhere and typing
                    await page.click('body')
                    await page.keyboard.type(search_query)
                    logger.info("🎭 Typed search query into focused element")
                
                # Set location
                logger.info(f"🎭 Setting location to: {location_zip}")
                location_selectors = [
                    'input[name="zip"]',  # Cars.com ZIP field (PRIORITY)
                    'input[data-testid="sitewide-search-filter-location"]',
                    'input[name="location"]',
                    'input[placeholder*="location"]',
                    'input[placeholder*="Location"]',
                    'input[placeholder*="zip"]',
                    'input[placeholder*="ZIP"]'
                ]
                
                location_filled = False
                for selector in location_selectors:
                    try:
                        location_input = page.locator(selector).first  # Use first matching element
                        if await location_input.count() > 0 and await location_input.is_visible():
                            await location_input.clear()
                            await location_input.fill(location_zip)
                            location_filled = True
                            logger.info(f"🎭 Successfully filled location: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"🎭 Failed to fill location {selector}: {str(e)}")
                        continue
                
                if not location_filled:
                    logger.warning("🎭 Could not set location")
                
                # Submit the search
                logger.info("🎭 Submitting search...")
                
                # Try multiple submission methods
                submitted = False
                
                # Method 1: Click search/submit button
                search_button_selectors = [
                    'button[data-testid="sitewide-search-submit"]',
                    'button[type="submit"]',
                    'input[type="submit"]',
                    '.search-button',
                    'button:has-text("Search")',
                    'button:has-text("Find")',
                    '[data-qa="search-button"]'
                ]
                
                for selector in search_button_selectors:
                    try:
                        button = page.locator(selector).first  # Use first matching element
                        if await button.count() > 0 and await button.is_visible():
                            await button.click()
                            submitted = True
                            logger.info(f"🎭 Clicked search button: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"🎭 Failed to click button {selector}: {str(e)}")
                        continue
                
                # Method 2: Press Enter on search input
                if not submitted:
                    # Define search selectors for Enter press
                    enter_selectors = [
                        'input[name="one_hitter"]',
                        'input[data-testid="sitewide-search-filter-text"]',
                        'input[name="searchTerm"]',
                        'input[placeholder*="Search"]'
                    ]
                    for selector in enter_selectors:
                        try:
                            search_input = page.locator(selector)
                            if await search_input.count() > 0:
                                await search_input.press("Enter")
                                submitted = True
                                logger.info(f"🎭 Pressed Enter on: {selector}")
                                break
                        except Exception as e:
                            logger.debug(f"🎭 Failed to press Enter on {selector}: {str(e)}")
                            continue
                
                # Method 3: Submit any form on the page
                if not submitted:
                    try:
                        forms = await page.locator('form').all()
                        if forms:
                            await forms[0].evaluate("form => form.submit()")
                            submitted = True
                            logger.info("🎭 Submitted first form on page")
                    except Exception as e:
                        logger.debug(f"🎭 Failed to submit form: {str(e)}")
                
                if submitted:
                    logger.info("🎭 Search submitted, waiting for results...")
                    await page.wait_for_load_state("networkidle", timeout=20000)
                    # Additional wait for dynamic content
                    await page.wait_for_timeout(3000)
                else:
                    logger.error("🎭 Could not submit search")
                    return []
            
            # Wait for results to load and log current URL
            current_url = page.url
            logger.info(f"🎭 Current page URL: {current_url}")
            
            # Check if we're on a results page
            if "results" in current_url or "search" in current_url or "shopping" in current_url:
                logger.info("🎭 Appears to be on a results page")
            else:
                logger.warning(f"🎭 Unexpected page URL: {current_url}")
            
            # Extract vehicle data with multiple approaches
            vehicles = []
            
            # Try different selectors for vehicle listings
            vehicle_selectors = [
                '[data-testid="listing-AVAILABLE"]',  # Original selector
                '.vehicle-card',
                '.listing',
                '.vehicle-listing',
                '.car-listing',
                '.search-result',
                '[data-qa="vehicle-card"]',
                '.vehicle-details',
                '.listing-card'
            ]
            
            vehicle_cards = []
            used_selector = None
            
            for selector in vehicle_selectors:
                try:
                    cards = await page.locator(selector).all()
                    if len(cards) > 0:
                        vehicle_cards = cards
                        used_selector = selector
                        logger.info(f"🎭 Found {len(vehicle_cards)} vehicle cards using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"🎭 Failed to find vehicles with {selector}: {str(e)}")
                    continue
            
            # If no cards found with specific selectors, try generic approach
            if not vehicle_cards:
                logger.warning("🎭 No vehicle cards found with specific selectors, trying generic approach...")
                
                # Look for any elements that might contain vehicle data
                potential_cards = await page.locator('div:has-text("$"), div:has-text("Honda"), div:has-text("Accord")').all()
                if potential_cards:
                    logger.info(f"🎭 Found {len(potential_cards)} potential vehicle elements")
                    vehicle_cards = potential_cards[:20]  # Limit to reasonable number
                    used_selector = "generic price/vehicle text"
            
            # If still no results, log page content for debugging
            if not vehicle_cards:
                logger.warning("🎭 No vehicle cards found, checking page content...")
                page_title = await page.title()
                logger.info(f"🎭 Page title: {page_title}")
                
                # Check if there's a "no results" message
                no_results_selectors = [
                    ':has-text("No results")',
                    ':has-text("no vehicles")',
                    ':has-text("0 results")',
                    '.no-results',
                    '.empty-results'
                ]
                
                for selector in no_results_selectors:
                    try:
                        no_results = await page.locator(selector).count()
                        if no_results > 0:
                            logger.info(f"🎭 Found 'no results' message: {selector}")
                            break
                    except:
                        continue
                
                # Get page text for debugging (first 500 chars)
                try:
                    page_text = await page.locator('body').text_content()
                    if page_text:
                        logger.debug(f"🎭 Page content preview: {page_text[:500]}...")
                except:
                    pass
            
            # Process found vehicle cards
            for i, card in enumerate(vehicle_cards[:20]):  # Limit to first 20 results
                try:
                    logger.debug(f"🎭 Processing vehicle card {i+1}/{len(vehicle_cards)}")
                    vehicle_data = await self._extract_cars_com_vehicle(card)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                        logger.info(f"🎭 Successfully extracted vehicle: {vehicle_data.get('make', 'Unknown')} {vehicle_data.get('model', 'Unknown')} - ${vehicle_data.get('price', 'Unknown')}")
                except Exception as e:
                    logger.debug(f"🎭 Error extracting vehicle {i+1}: {str(e)}")
                    continue
            
            logger.info(f"🎭 Successfully extracted {len(vehicles)} vehicles from {len(vehicle_cards)} cards")
            return vehicles
            
        except Exception as e:
            logger.error(f"🎭 Cars.com scraping error: {str(e)}")
            return []
    
    async def _extract_cars_com_vehicle(self, card) -> Optional[Dict[str, Any]]:
        """Extract vehicle data from Cars.com listing card"""
        try:
            vehicle_data = {
                "source": "cars.com",
                "discovered_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "images": [],
                "features": []
            }
            
            # Get all text content for debugging
            card_text = await card.text_content()
            logger.debug(f"🎭 Card text content: {card_text[:200]}...")
            
            # Extract price with multiple selectors
            price_selectors = [
                '[data-testid="listing-price"]',
                '.price',
                '.listing-price',
                '.vehicle-price',
                ':has-text("$")'
            ]
            
            price_found = False
            for selector in price_selectors:
                try:
                    price_element = card.locator(selector)
                    if await price_element.count() > 0:
                        price_text = await price_element.text_content()
                        if price_text and '$' in price_text:
                            # Extract numeric price
                            import re
                            price_match = re.search(r'\$([0-9,]+)', price_text)
                            if price_match:
                                vehicle_data["price"] = int(price_match.group(1).replace(',', ''))
                                price_found = True
                                logger.debug(f"🎭 Found price: ${vehicle_data['price']} using {selector}")
                                break
                except Exception as e:
                    logger.debug(f"🎭 Failed to extract price with {selector}: {str(e)}")
                    continue
            
            # If no price found with selectors, try text content search
            if not price_found and card_text:
                import re
                price_match = re.search(r'\$([0-9,]+)', card_text)
                if price_match:
                    vehicle_data["price"] = int(price_match.group(1).replace(',', ''))
                    price_found = True
                    logger.debug(f"🎭 Found price from text content: ${vehicle_data['price']}")
            
            # Extract year, make, model with multiple selectors
            title_selectors = [
                '[data-testid="listing-title"]',
                '.listing-title',
                '.vehicle-title',
                '.car-title',
                'h2', 'h3', 'h4'
            ]
            
            title_found = False
            for selector in title_selectors:
                try:
                    title_element = card.locator(selector)
                    if await title_element.count() > 0:
                        title_text = await title_element.text_content()
                        if title_text and any(word in title_text.lower() for word in ['honda', 'accord', '2016', '2017', '2018', '2019', '2020', '2021']):
                            # Parse title like "2019 Honda Accord EX"
                            title_parts = title_text.strip().split()
                            if len(title_parts) >= 3:
                                year_candidate = title_parts[0]
                                if year_candidate.isdigit() and 2000 <= int(year_candidate) <= 2030:
                                    vehicle_data["year"] = int(year_candidate)
                                    vehicle_data["make"] = title_parts[1]
                                    vehicle_data["model"] = title_parts[2]
                                    title_found = True
                                    logger.debug(f"🎭 Found title: {title_text} using {selector}")
                                    break
                except Exception as e:
                    logger.debug(f"🎭 Failed to extract title with {selector}: {str(e)}")
                    continue
            
            # If no title found with selectors, try text content search
            if not title_found and card_text:
                import re
                # Look for year patterns
                year_match = re.search(r'\b(20[0-2][0-9])\b', card_text)
                if year_match:
                    vehicle_data["year"] = int(year_match.group(1))
                
                # Look for Honda/Accord specifically
                if 'honda' in card_text.lower():
                    vehicle_data["make"] = "Honda"
                if 'accord' in card_text.lower():
                    vehicle_data["model"] = "Accord"
                
                if "make" in vehicle_data and "model" in vehicle_data:
                    title_found = True
                    logger.debug(f"🎭 Found make/model from text content")
            
            # Extract mileage with multiple selectors
            mileage_selectors = [
                '[data-testid="listing-mileage"]',
                '.mileage',
                '.listing-mileage',
                ':has-text("miles")',
                ':has-text("mi")'
            ]
            
            for selector in mileage_selectors:
                try:
                    mileage_element = card.locator(selector)
                    if await mileage_element.count() > 0:
                        mileage_text = await mileage_element.text_content()
                        if mileage_text:
                            # Extract numeric mileage
                            import re
                            mileage_match = re.search(r'([0-9,]+)', mileage_text)
                            if mileage_match:
                                vehicle_data["mileage"] = int(mileage_match.group(1).replace(',', ''))
                                logger.debug(f"🎭 Found mileage: {vehicle_data['mileage']} using {selector}")
                                break
                except Exception as e:
                    logger.debug(f"🎭 Failed to extract mileage with {selector}: {str(e)}")
                    continue
            
            # Extract location with multiple selectors
            location_selectors = [
                '[data-testid="listing-dealer-city-state"]',
                '.location',
                '.dealer-location',
                '.listing-location'
            ]
            
            for selector in location_selectors:
                try:
                    location_element = card.locator(selector)
                    if await location_element.count() > 0:
                        location_text = await location_element.text_content()
                        if location_text:
                            vehicle_data["location"] = location_text.strip()
                            logger.debug(f"🎭 Found location: {vehicle_data['location']} using {selector}")
                            break
                except Exception as e:
                    logger.debug(f"🎭 Failed to extract location with {selector}: {str(e)}")
                    continue
            
            # Extract URL
            link_selectors = [
                'a[href*="/vehicledetail/"]',
                'a[href*="/vehicle/"]',
                'a[href*="/listing/"]',
                'a'
            ]
            
            for selector in link_selectors:
                try:
                    link_element = card.locator(selector)
                    if await link_element.count() > 0:
                        href = await link_element.get_attribute('href')
                        if href and ('vehicle' in href or 'listing' in href):
                            vehicle_data["url"] = href if href.startswith('http') else f"https://www.cars.com{href}"
                            logger.debug(f"🎭 Found URL: {vehicle_data['url']} using {selector}")
                            break
                except Exception as e:
                    logger.debug(f"🎭 Failed to extract URL with {selector}: {str(e)}")
                    continue
            
            # Generate external ID if we have enough data
            if "make" in vehicle_data and "model" in vehicle_data:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                price_part = vehicle_data.get("price", "unknown")
                year_part = vehicle_data.get("year", "unknown")
                vehicle_data["external_id"] = f"{vehicle_data['make']}_{vehicle_data['model']}_{year_part}_{price_part}_{timestamp}"
            
            # Only return if we have essential data (at least make or price)
            if "price" in vehicle_data or "make" in vehicle_data:
                logger.debug(f"🎭 Successfully extracted vehicle data: {vehicle_data}")
                return vehicle_data
            else:
                logger.debug("🎭 Not enough data extracted to create vehicle record")
                return None
            
        except Exception as e:
            logger.debug(f"🎭 Error extracting Cars.com vehicle data: {str(e)}")
            return None
    
    async def _scrape_edmunds(self, page: Page, criteria: SearchCriteria, location_zip: str) -> List[Dict[str, Any]]:
        """Scrape Edmunds using form automation"""
        try:
            logger.info("🎭 Navigating to Edmunds...")
            await page.goto("https://www.edmunds.com/inventory/", wait_until="domcontentloaded")
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            # Edmunds search implementation would go here
            # For now, return empty list as placeholder
            logger.info("🎭 Edmunds scraper - implementation in progress")
            return []
            
        except Exception as e:
            logger.error(f"🎭 Edmunds scraping error: {str(e)}")
            return []
    
    async def _scrape_cargurus(self, page: Page, criteria: SearchCriteria, location_zip: str) -> List[Dict[str, Any]]:
        """Scrape CarGurus using form automation"""
        try:
            logger.info("🎭 Navigating to CarGurus...")
            await page.goto("https://www.cargurus.com/Cars/", wait_until="domcontentloaded")
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            # CarGurus search implementation would go here
            # For now, return empty list as placeholder
            logger.info("🎭 CarGurus scraper - implementation in progress")
            return []
            
        except Exception as e:
            logger.error(f"🎭 CarGurus scraping error: {str(e)}")
            return []
    
    async def search_all_marketplaces(self, criteria: SearchCriteria, location_zips: List[str] = None) -> List[ScrapingResult]:
        """
        Search all supported marketplaces concurrently
        
        Args:
            criteria: Search criteria
            location_zips: List of ZIP codes to search
            
        Returns:
            List of ScrapingResult objects
        """
        if not location_zips:
            location_zips = ["33101"]  # Default to Miami, FL
        
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
                logger.error(f"🎭 Task failed with exception: {result}")
        
        return valid_results 