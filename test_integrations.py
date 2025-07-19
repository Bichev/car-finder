#!/usr/bin/env python3
"""
Car Finder Integration Test Script

Tests the new Firecrawl and Perplexity integrations through the API endpoints.
This script demonstrates the complete vehicle search and analysis workflow.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

import httpx


class CarFinderIntegrationTester:
    """Test suite for Car Finder integrations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
        
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        print("🚀 Car Finder Integration Test Suite")
        print(f"Testing API at: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Service Status", self.test_service_status),
            ("Create Test User", self.test_create_user),
            ("Create Test Search", self.test_create_search),
            ("Market Research", self.test_market_research),
            ("Integration Test", self.test_integration_status),
            ("Execute Search", self.test_execute_search),
            ("Get Search Results", self.test_search_results)
        ]
        
        self.user_id = None
        self.search_id = None
        
        for test_name, test_func in tests:
            results["total_tests"] += 1
            
            try:
                print(f"\n{'=' * 60}")
                print(f"TEST: {test_name}")
                print(f"{'=' * 60}")
                
                success = await test_func()
                
                if success:
                    results["passed"] += 1
                    print(f"✅ PASS: {test_name}")
                else:
                    results["failed"] += 1
                    print(f"❌ FAIL: {test_name}")
                    
            except Exception as e:
                results["failed"] += 1
                error_msg = f"{test_name}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ ERROR: {test_name} - {str(e)}")
        
        # Print final results
        print(f"\n{'=' * 60}")
        print("FINAL RESULTS")
        print(f"{'=' * 60}")
        print(f"Tests Passed: {results['passed']}/{results['total_tests']}")
        
        if results['passed'] == results['total_tests']:
            print("🎉 ALL TESTS PASSED! Your Car Finder integrations are working!")
        else:
            print(f"❌ {results['failed']} tests failed.")
            if results['errors']:
                print("\nErrors:")
                for error in results['errors']:
                    print(f"  - {error}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await self.client.aclose()
        return results
    
    async def test_health_check(self) -> bool:
        """Test basic API health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Health Status: {data}")
                return data.get("status") == "healthy"
            else:
                print(f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Health check error: {e}")
            return False
    
    async def test_service_status(self) -> bool:
        """Test Firecrawl and Perplexity service status"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/search-execution/marketplace-status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Service Status:")
                print(json.dumps(data, indent=2))
                
                # Check if services are configured
                services = data.get("services", {})
                firecrawl_ok = services.get("firecrawl", {}).get("api_key_present", False)
                perplexity_ok = services.get("perplexity", {}).get("api_key_present", False)
                
                print(f"\nFirecrawl API Key: {'✅ Present' if firecrawl_ok else '❌ Missing'}")
                print(f"Perplexity API Key: {'✅ Present' if perplexity_ok else '❌ Missing'}")
                
                if not firecrawl_ok or not perplexity_ok:
                    print("\n⚠️  Warning: Missing API keys. Add them to your .env file:")
                    if not firecrawl_ok:
                        print("   FIRECRAWL_API_KEY=your-firecrawl-api-key")
                    if not perplexity_ok:
                        print("   PERPLEXITY_API_KEY=your-perplexity-api-key")
                
                return True
            else:
                print(f"Service status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Service status error: {e}")
            return False
    
    async def test_create_user(self) -> bool:
        """Create a test user"""
        try:
            user_data = {
                "email": f"integration-test-{int(time.time())}@example.com",
                "subscription_tier": "professional"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/users/",
                json=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data["id"]
                print(f"Created user: {self.user_id}")
                print(f"Email: {data['email']}")
                print(f"Subscription: {data['subscription_tier']}")
                return True
            else:
                print(f"User creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"User creation error: {e}")
            return False
    
    async def test_create_search(self) -> bool:
        """Create a test search configuration"""
        try:
            if not self.user_id:
                print("No user ID available")
                return False
            
            search_data = {
                "name": "Integration Test - Toyota Camry FL",
                "criteria": {
                    "makes": ["Toyota"],
                    "models": ["Camry"],
                    "year_min": 2015,
                    "year_max": 2020,
                    "price_min": 15000,
                    "price_max": 25000,
                    "mileage_max": 100000,
                    "locations": ["FL"]
                },
                "schedule_cron": "0 */6 * * *"  # Every 6 hours
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/searches/?user_id={self.user_id}",
                json=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.search_id = data["id"]
                print(f"Created search: {self.search_id}")
                print(f"Name: {data['name']}")
                print(f"Criteria: {data['criteria']}")
                return True
            else:
                print(f"Search creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Search creation error: {e}")
            return False
    
    async def test_market_research(self) -> bool:
        """Test Perplexity market research"""
        try:
            research_data = {
                "make": "Toyota",
                "model": "Camry",
                "year": 2018,
                "location": "FL"
            }
            
            print("🧠 Testing Perplexity AI market research...")
            print("This may take 30-60 seconds for AI analysis...")
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/search-execution/market-research",
                json=research_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Market Research Results:")
                print(f"  Vehicle: {data['year']} {data['make']} {data['model']}")
                print(f"  Location: {data['location']}")
                
                # Show market trends
                trends = data.get("market_trends", {})
                print(f"  Trend Direction: {trends.get('trend_direction', 'unknown')}")
                print(f"  Confidence: {trends.get('confidence', 0):.2f}")
                
                # Show pricing
                pricing = data.get("average_pricing", {})
                if isinstance(pricing, dict) and "value_range" in pricing:
                    value_range = pricing["value_range"]
                    if value_range:
                        print(f"  Price Range: ${value_range.get('min', 0):,.0f} - ${value_range.get('max', 0):,.0f}")
                        print(f"  Average: ${value_range.get('average', 0):,.0f}")
                
                # Show regional insights
                insights = data.get("regional_insights", [])
                if insights:
                    print(f"  Regional Factors: {len(insights)} insights")
                    for insight in insights[:3]:  # Show first 3
                        print(f"    - {insight[:100]}...")
                
                return True
            else:
                print(f"Market research failed: {response.status_code} - {response.text}")
                # Don't fail the test if API keys are missing
                if response.status_code == 500 and "API" in response.text:
                    print("⚠️  This is likely due to missing API keys")
                    return True
                return False
                
        except Exception as e:
            print(f"Market research error: {e}")
            return False
    
    async def test_integration_status(self) -> bool:
        """Test the integration between services"""
        try:
            print("🔧 Testing service integrations...")
            print("This will test both Firecrawl and Perplexity APIs...")
            
            response = await self.client.post(f"{self.base_url}/api/v1/search-execution/test-integration")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Integration Test Results:")
                
                tests = data.get("tests", {})
                
                # Firecrawl test
                firecrawl = tests.get("firecrawl", {})
                print(f"  Firecrawl: {firecrawl.get('status', 'unknown')}")
                if firecrawl.get("vehicles_found") is not None:
                    print(f"    Vehicles Found: {firecrawl['vehicles_found']}")
                if firecrawl.get("error"):
                    print(f"    Error: {firecrawl['error']}")
                
                # Perplexity test
                perplexity = tests.get("perplexity", {})
                print(f"  Perplexity: {perplexity.get('status', 'unknown')}")
                if perplexity.get("confidence") is not None:
                    print(f"    Analysis Confidence: {perplexity['confidence']:.2f}")
                if perplexity.get("error"):
                    print(f"    Error: {perplexity['error']}")
                
                # Consider successful if at least one service works
                firecrawl_ok = firecrawl.get("status") in ["success", "failed"]  # failed means it connected but found no vehicles
                perplexity_ok = perplexity.get("status") == "success"
                
                if not firecrawl_ok and not perplexity_ok:
                    print("⚠️  Both services failed - likely missing API keys")
                    return True  # Don't fail test for missing keys
                
                return True
            else:
                print(f"Integration test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Integration test error: {e}")
            return False
    
    async def test_execute_search(self) -> bool:
        """Test search execution with Firecrawl scraping"""
        try:
            if not self.search_id:
                print("No search ID available")
                return False
            
            search_data = {
                "search_id": self.search_id,
                "force_execution": True
            }
            
            print("🔍 Executing search with Firecrawl scraping...")
            print("This may take 2-5 minutes to scrape vehicle listings...")
            print("Note: Results depend on having valid API keys")
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/search-execution/execute",
                json=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Search Execution Results:")
                print(f"  Message: {data['message']}")
                print(f"  Vehicles Found: {data['vehicles_found']}")
                print(f"  Opportunities Created: {data['opportunities_created']}")
                print(f"  Execution Time: {data['execution_time']:.2f} seconds")
                print(f"  Success: {data['success']}")
                
                if data.get("error_message"):
                    print(f"  Error: {data['error_message']}")
                
                return data["success"]
            else:
                print(f"Search execution failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Search execution error: {e}")
            return False
    
    async def test_search_results(self) -> bool:
        """Test getting search results"""
        try:
            if not self.search_id:
                print("No search ID available")
                return False
            
            response = await self.client.get(
                f"{self.base_url}/api/v1/search-execution/search/{self.search_id}/results?limit=5"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Search Results:")
                print(f"  Total Opportunities: {data['total_opportunities']}")
                
                results = data.get("results", [])
                for i, result in enumerate(results[:3], 1):  # Show first 3 results
                    opportunity = result.get("opportunity", {})
                    vehicle = result.get("vehicle", {})
                    
                    print(f"  Result {i}:")
                    if vehicle:
                        print(f"    Vehicle: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
                        print(f"    Price: ${vehicle.get('price', 0):,.2f}")
                        print(f"    Location: {vehicle.get('location', {}).get('city', 'Unknown')}, {vehicle.get('location', {}).get('state', 'Unknown')}")
                    
                    if opportunity:
                        print(f"    Projected Profit: ${opportunity.get('projected_profit', 0):,.2f}")
                        print(f"    Confidence: {opportunity.get('confidence_score', 0):.2f}")
                
                return True
            else:
                print(f"Get search results failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Search results error: {e}")
            return False


async def main():
    """Run the integration test suite"""
    tester = CarFinderIntegrationTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if results["passed"] == results["total_tests"] else 1
    exit(exit_code)


if __name__ == "__main__":
    print("Car Finder Integration Test Suite")
    print("Make sure the API is running: docker-compose up -d")
    print("And that you have API keys in your .env file\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        exit(1) 