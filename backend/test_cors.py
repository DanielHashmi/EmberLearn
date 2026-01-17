#!/usr/bin/env python3
"""Test CORS configuration."""

import requests

BASE_URL = "http://localhost:8000"

def test_cors():
    """Test CORS headers."""
    print("Testing CORS configuration...")
    
    # Test preflight request
    print("\n1. Testing OPTIONS request (preflight)...")
    response = requests.options(
        f"{BASE_URL}/api/exercises",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization"
        }
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"     {header}: {value}")
    
    # Test actual request
    print("\n2. Testing GET request...")
    response = requests.get(
        f"{BASE_URL}/api/exercises",
        headers={"Origin": "http://localhost:3000"}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"     {header}: {value}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Received {len(data)} exercises")
    else:
        print(f"   ✗ Error: {response.text}")

if __name__ == "__main__":
    test_cors()
