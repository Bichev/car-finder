#!/usr/bin/env python3
"""
Car Finder API Test Script
This script tests the basic functionality of the Car Finder API
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def print_step(step, description):
    """Print a test step"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print('='*60)

def print_result(success, message, data=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")

def test_health_check():
    """Test health check endpoint"""
    print_step(1, "Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Health check passed", data)
            return True
        else:
            print_result(False, f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Health check failed: {str(e)}")
        return False

def test_create_user():
    """Test user creation"""
    print_step(2, "Create User")
    user_data = {
        "email": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}@example.com",
        "subscription_tier": "professional"
    }
    
    try:
        response = requests.post(f"{API_BASE}/users/", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User created successfully", data)
            return data['id']
        else:
            print_result(False, f"User creation failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print_result(False, f"User creation failed: {str(e)}")
        return None

def test_get_user(user_id):
    """Test getting user by ID"""
    print_step(3, "Get User")
    try:
        response = requests.get(f"{API_BASE}/users/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User retrieved successfully", data)
            return True
        else:
            print_result(False, f"Get user failed with status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Get user failed: {str(e)}")
        return False

def test_create_search(user_id):
    """Test search creation"""
    print_step(4, "Create Search Configuration")
    search_data = {
        "name": "Test Florida Toyota Search",
        "criteria": {
            "makes": ["Toyota"],
            "models": ["Camry", "Corolla"],
            "year_min": 2015,
            "year_max": 2022,
            "price_min": 15000,
            "price_max": 30000,
            "locations": ["FL"]
        },
        "schedule_cron": "0 */2 * * *"
    }
    
    try:
        response = requests.post(f"{API_BASE}/searches/?user_id={user_id}", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Search created successfully", data)
            return data['id']
        else:
            print_result(False, f"Search creation failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print_result(False, f"Search creation failed: {str(e)}")
        return None

def test_list_searches(user_id):
    """Test listing searches"""
    print_step(5, "List User Searches")
    try:
        response = requests.get(f"{API_BASE}/searches/?user_id={user_id}")
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Found {data['total']} searches", data)
            return True
        else:
            print_result(False, f"List searches failed with status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"List searches failed: {str(e)}")
        return False

def test_vehicle_stats():
    """Test vehicle statistics endpoint"""
    print_step(6, "Vehicle Statistics")
    try:
        response = requests.get(f"{API_BASE}/vehicles/stats/summary")
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Vehicle stats retrieved (empty is expected)", data)
            return True
        else:
            print_result(False, f"Vehicle stats failed with status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Vehicle stats failed: {str(e)}")
        return False

def test_opportunities_summary():
    """Test opportunities summary endpoint"""
    print_step(7, "Opportunities Summary")
    try:
        response = requests.get(f"{API_BASE}/opportunities/stats/summary")
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Opportunities summary retrieved (empty is expected)", data)
            return True
        else:
            print_result(False, f"Opportunities summary failed with status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Opportunities summary failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Car Finder API Test Script")
    print(f"Testing API at: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track test results
    tests_passed = 0
    total_tests = 7
    
    # Run tests
    if test_health_check():
        tests_passed += 1
    
    user_id = test_create_user()
    if user_id:
        tests_passed += 1
        
        if test_get_user(user_id):
            tests_passed += 1
        
        search_id = test_create_search(user_id)
        if search_id:
            tests_passed += 1
        
        if test_list_searches(user_id):
            tests_passed += 1
    else:
        print_result(False, "Skipping user-dependent tests due to user creation failure")
    
    if test_vehicle_stats():
        tests_passed += 1
    
    if test_opportunities_summary():
        tests_passed += 1
    
    # Final results
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print('='*60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Your Car Finder API is working perfectly!")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs to explore the interactive API docs")
        print("2. Ready to implement Firecrawl and Perplexity integrations!")
        return 0
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure Docker containers are running: docker-compose ps")
        print("2. Check logs: docker-compose logs -f app")
        print("3. Verify your .env file is properly configured")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 