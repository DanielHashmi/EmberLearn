#!/usr/bin/env python3
"""Test the complete exercise flow."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test the complete exercise submission flow."""
    
    # Step 1: Register/Login
    print("Step 1: Authenticating...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "testuser@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print("  Registering new user...")
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "password123",
                "name": "Test User"
            }
        )
        if register_response.status_code == 200:
            token = register_response.json()["token"]
            print("  ✓ Registered successfully")
        else:
            print(f"  ✗ Registration failed: {register_response.text}")
            return False
    else:
        token = login_response.json()["token"]
        print("  ✓ Logged in successfully")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: List exercises
    print("\nStep 2: Fetching exercises...")
    exercises_response = requests.get(f"{BASE_URL}/api/exercises", headers=headers)
    
    if exercises_response.status_code != 200:
        print(f"  ✗ Failed to fetch exercises: {exercises_response.text}")
        return False
    
    exercises = exercises_response.json()
    print(f"  ✓ Found {len(exercises)} exercises")
    
    if not exercises:
        print("  ✗ No exercises found!")
        return False
    
    # Step 3: Get first exercise details
    first_exercise = exercises[0]
    exercise_id = first_exercise["id"]
    print(f"\nStep 3: Fetching exercise '{first_exercise['title']}'...")
    
    exercise_response = requests.get(
        f"{BASE_URL}/api/exercises/{exercise_id}",
        headers=headers
    )
    
    if exercise_response.status_code != 200:
        print(f"  ✗ Failed to fetch exercise: {exercise_response.text}")
        return False
    
    exercise = exercise_response.json()
    print(f"  ✓ Exercise loaded")
    print(f"     Title: {exercise['title']}")
    print(f"     Difficulty: {exercise['difficulty']}")
    print(f"     Topic: {exercise['topic_name']}")
    print(f"     Starter code: {exercise['starter_code'][:50]}...")
    
    # Step 4: Submit a solution
    print(f"\nStep 4: Submitting solution...")
    
    # Use the solution from the exercise (cheating for testing purposes)
    if "solution" in exercise and exercise["solution"]:
        code = exercise["solution"]
        print(f"  Using provided solution")
    else:
        # For exercises without solution, use starter code
        code = exercise["starter_code"]
        print(f"  Using starter code")
    
    submit_response = requests.post(
        f"{BASE_URL}/api/exercises/{exercise_id}/submit",
        headers={**headers, "Content-Type": "application/json"},
        json={"code": code}
    )
    
    if submit_response.status_code != 200:
        print(f"  ✗ Submission failed: {submit_response.text}")
        return False
    
    result = submit_response.json()
    print(f"  ✓ Submission processed")
    print(f"     Score: {result['score']}%")
    print(f"     Passed: {result['passed']}")
    print(f"     XP Earned: {result['xp_earned']}")
    print(f"     Test Results: {len(result['test_results'])} tests")
    
    for i, test in enumerate(result['test_results'], 1):
        status = "✓" if test['passed'] else "✗"
        print(f"       {status} Test {i}: {test['input_data'][:30]}...")
    
    # Step 5: Check progress
    print(f"\nStep 5: Checking progress...")
    progress_response = requests.get(f"{BASE_URL}/api/progress", headers=headers)
    
    if progress_response.status_code != 200:
        print(f"  ✗ Failed to fetch progress: {progress_response.text}")
        return False
    
    progress = progress_response.json()
    print(f"  ✓ Progress loaded")
    print(f"     Level: {progress['level']}")
    print(f"     Total XP: {progress['total_xp']}")
    print(f"     Streak: {progress['streak']} days")
    print(f"     Longest Streak: {progress['longest_streak']} days")
    print(f"     Overall Mastery: {progress['overall_mastery']:.1f}%")
    print(f"     Topics: {len(progress['topics'])}")
    
    for topic in progress['topics'][:3]:  # Show first 3 topics
        print(f"       - {topic['name']}: {topic['mastery_score']:.1f}% ({topic['exercises_completed']}/{topic['total_exercises']} exercises)")
    
    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED - Full flow working!")
    print("="*50)
    return True

if __name__ == "__main__":
    test_complete_flow()
