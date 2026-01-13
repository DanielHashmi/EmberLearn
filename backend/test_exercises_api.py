#!/usr/bin/env python3
"""Quick test script to verify exercises API."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_exercises_list():
    """Test listing exercises without authentication."""
    print("Testing GET /api/exercises (no auth)...")
    response = requests.get(f"{BASE_URL}/api/exercises")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} exercises")
        if data:
            print(f"\nFirst exercise:")
            print(json.dumps(data[0], indent=2))
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_exercises_with_auth():
    """Test listing exercises with authentication."""
    print("\n\nTesting GET /api/exercises (with auth)...")
    
    # First login
    print("Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print("Login failed, trying to register...")
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User"
            }
        )
        if register_response.status_code == 200:
            token = register_response.json()["token"]
            print("Registered successfully")
        else:
            print(f"Registration failed: {register_response.text}")
            return False
    else:
        token = login_response.json()["token"]
        print("Logged in successfully")
    
    # Now fetch exercises with token
    print("\nFetching exercises with auth token...")
    response = requests.get(
        f"{BASE_URL}/api/exercises",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} exercises")
        if data:
            print(f"\nFirst exercise:")
            print(json.dumps(data[0], indent=2))
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    test_exercises_list()
    test_exercises_with_auth()
