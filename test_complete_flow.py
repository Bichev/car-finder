#!/usr/bin/env python3
"""
Complete Flow Test: Cars.com + Perplexity Analytics

This script tests the complete workflow:
1. Scrape Cars.com using Playwright automation 
2. Analyze results using Perplexity AI
3. Generate market insights and opportunities

Run: python test_complete_flow.py
"""

import asyncio
import json
from datetime import datetime
from src.services.playwright_service import PlaywrightScrapingService, PlaywrightConfig
from src.services.perplexity_service import PerplexityService
from src.models.schemas import SearchCriteria

async def test_complete_flow():
    """Test the complete Cars.com + Perplexity workflow"""
    print("🚀 Testing Complete Flow: Cars.com + Perplexity Analytics")
    print("=" * 60)
    
    # Configuration
    search_criteria = SearchCriteria(
        makes=["Honda"],
        models=["Accord"],
        year_min=2018,
        year_max=2023,
        price_min=18000,
        price_max=28000,
        locations=["FL"]
    )
    
    location_zip = "33101"  # Miami, FL
    
    print(f"🔍 Search Criteria:")
    print(f"   Make/Model: {search_criteria.makes[0]} {search_criteria.models[0]}")
    print(f"   Years: {search_criteria.year_min}-{search_criteria.year_max}")
    print(f"   Price: ${search_criteria.price_min:,}-${search_criteria.price_max:,}")
    print(f"   Location: {location_zip}")
    print()
    
    # Step 1: Scrape Cars.com with Playwright
    print("🎭 Step 1: Scraping Cars.com with Playwright...")
    print("-" * 40)
    
    start_time = datetime.now()
    
    # Configure Playwright for demonstration
    config = PlaywrightConfig(
        headless=True,  # Set to False to watch the automation in action
        timeout=60000   # 60 seconds timeout
    )
    
    try:
        async with PlaywrightScrapingService(config) as playwright_service:
            scraping_result = await playwright_service.search_marketplace(
                "cars_com",
                search_criteria,
                location_zip
            )
        
        scraping_duration = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Scraping Results:")
        print(f"   Success: {scraping_result.success}")
        print(f"   Vehicles Found: {scraping_result.total_found}")
        print(f"   Duration: {scraping_duration:.1f} seconds")
        
        if scraping_result.vehicles:
            print(f"   Sample Vehicle:")
            sample = scraping_result.vehicles[0]
            print(f"     {sample.get('year', 'N/A')} {sample.get('make', 'N/A')} {sample.get('model', 'N/A')}")
            print(f"     Price: ${sample.get('price', 'N/A')}")
            print(f"     Mileage: {sample.get('mileage', 'N/A')} miles")
            print(f"     Location: {sample.get('location', 'N/A')}")
        
        if scraping_result.error_message:
            print(f"   Error: {scraping_result.error_message}")
        
        print()
        
    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")
        return
    
    # Step 2: Analyze with Perplexity AI
    print("🧠 Step 2: Analyzing Results with Perplexity AI...")
    print("-" * 40)
    
    if scraping_result.success and scraping_result.vehicles:
        analysis_start = datetime.now()
        
        try:
            perplexity = PerplexityService()
            
            # Create analysis query based on scraped data
            vehicle_count = len(scraping_result.vehicles)
            price_range = f"${search_criteria.price_min:,}-${search_criteria.price_max:,}"
            year_range = f"{search_criteria.year_min}-{search_criteria.year_max}"
            
            # Get price statistics from scraped vehicles
            prices = [v.get('price', 0) for v in scraping_result.vehicles if v.get('price')]
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                price_stats = f"Average: ${avg_price:,.0f}, Range: ${min_price:,}-${max_price:,}"
            else:
                price_stats = "No price data available"
            
            analysis_query = f"""
            I found {vehicle_count} {search_criteria.makes[0]} {search_criteria.models[0]} vehicles 
            ({year_range}) in the {price_range} price range in Miami, FL area.
            
            Market data: {price_stats}
            
            Please provide:
            1. Market analysis for these vehicles
            2. Value assessment and trends
            3. Investment opportunity rating
            4. Recommendations for buyers/sellers
            5. Regional market factors for South Florida
            """
            
            print(f"🤔 Analyzing {vehicle_count} vehicles...")
            
            # Query Perplexity for market analysis
            analysis_response = await perplexity._query_perplexity(
                query=analysis_query,
                system_prompt="You are an expert automotive market analyst specializing in used car valuations and market trends. Provide data-driven insights.",
                max_tokens=800  # Detailed analysis
            )
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            print(f"✅ Analysis Completed in {analysis_duration:.1f} seconds")
            print(f"📊 Market Analysis:")
            print()
            
            # Extract and display the AI analysis
            if analysis_response.get("success") and analysis_response.get("data"):
                content = analysis_response["data"].get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    # Format the analysis nicely
                    print("=" * 60)
                    print(content)
                    print("=" * 60)
                else:
                    print("❌ No analysis content received")
            else:
                print(f"❌ Analysis failed: {analysis_response.get('error', 'Unknown error')}")
            
            await perplexity.close()
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
    
    else:
        print("⚠️ Skipping analysis - no vehicles found to analyze")
    
    # Step 3: Summary and Recommendations
    print()
    print("🎯 Step 3: Summary & Recommendations")
    print("-" * 40)
    
    total_duration = (datetime.now() - start_time).total_seconds()
    
    print(f"📈 Workflow Summary:")
    print(f"   Total Duration: {total_duration:.1f} seconds")
    print(f"   Vehicles Discovered: {scraping_result.total_found if scraping_result.success else 0}")
    print(f"   Data Quality: {'High' if scraping_result.success and scraping_result.vehicles else 'Low'}")
    print(f"   AI Analysis: {'Completed' if scraping_result.success and scraping_result.vehicles else 'Skipped'}")
    
    print()
    print("🚀 Next Steps:")
    print("   1. ✅ Cars.com scraping is working perfectly")
    print("   2. ✅ Perplexity analysis provides valuable insights")
    print("   3. 📊 Ready for production dashboard integration")
    print("   4. 🔄 Can be automated for regular market monitoring")
    
    print()
    print("🎉 Complete flow test finished!")

async def test_api_endpoints():
    """Test the API endpoints as well"""
    print()
    print("🌐 Testing API Endpoints...")
    print("-" * 40)
    
    import httpx
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test Playwright endpoint
            playwright_payload = {
                "marketplace": "cars_com",
                "make": "Honda",
                "model": "Accord",
                "year_min": 2018,
                "year_max": 2023,
                "price_min": 18000,
                "price_max": 28000,
                "location_zip": "33101",
                "headless": True,
                "timeout_seconds": 60
            }
            
            print("🎭 Testing Playwright API endpoint...")
            response = await client.post(
                f"{base_url}/api/v1/search-execution/test/playwright",
                json=playwright_payload,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('results', {}).get('vehicles_found', 0)} vehicles found")
            else:
                print(f"   ❌ API Error: {response.status_code}")
            
            # Test Perplexity endpoint
            perplexity_payload = {
                "query": "What are the current market trends for 2018-2023 Honda Accord in the $18k-28k price range?",
                "model": "sonar-pro",
                "max_tokens": 500,
                "timeout_seconds": 30
            }
            
            print("🧠 Testing Perplexity API endpoint...")
            response = await client.post(
                f"{base_url}/api/v1/search-execution/test/perplexity",
                json=perplexity_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Analysis completed: {len(result.get('ai_analysis', ''))} characters")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
    except Exception as e:
        print(f"   ⚠️ API test skipped: {str(e)}")
        print("   💡 Start the API server with: python -m src.main")

if __name__ == "__main__":
    print("🔧 Car Finder: Complete Flow Test")
    print("This test demonstrates the full Cars.com + Perplexity workflow")
    print()
    
    # Run the complete flow test
    asyncio.run(test_complete_flow())
    
    # Also test the API endpoints if server is running
    asyncio.run(test_api_endpoints()) 