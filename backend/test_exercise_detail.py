"""Test that exercise detail endpoint works without authentication."""

import requests

BASE_URL = "http://localhost:8000"

# First get list of exercises
print("=" * 60)
print("Fetching exercise list...")
response = requests.get(f"{BASE_URL}/api/exercises")

if response.status_code == 200:
    exercises = response.json()
    print(f"✓ Found {len(exercises)} exercises")

    if exercises:
        first_exercise = exercises[0]
        exercise_id = first_exercise['id']

        print(f"\nFirst exercise:")
        print(f"  ID: {exercise_id}")
        print(f"  Title: {first_exercise['title']}")

        # Test detail endpoint WITHOUT authentication
        print(f"\n{'=' * 60}")
        print(f"Testing GET /api/exercises/{exercise_id} (NO AUTH)...")
        detail_response = requests.get(f"{BASE_URL}/api/exercises/{exercise_id}")

        print(f"Status: {detail_response.status_code}")
        if detail_response.status_code == 200:
            detail = detail_response.json()
            print(f"✓ Exercise loaded successfully")
            print(f"  Title: {detail['title']}")
            print(f"  Description: {detail['description'][:50]}...")
            print(f"  Starter code: {detail['starter_code'][:50]}...")
            print(f"  Completed: {detail['completed']}")
            print(f"  Best score: {detail['best_score']}")
        elif detail_response.status_code == 401:
            print("✗ Error: Authentication required (this is the bug!)")
            print(f"  Response: {detail_response.text}")
        else:
            print(f"✗ Error: {detail_response.status_code}")
            print(f"  Response: {detail_response.text}")
else:
    print(f"✗ Failed to fetch exercises: {response.status_code}")
    print(f"  Response: {response.text}")

print(f"\n{'=' * 60}")
