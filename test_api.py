#!/usr/bin/env python3
"""
Simple test script for the Bajaj Hackathon API
"""

import requests
import json

# API Configuration
API_URL = "http://localhost:8000/api/v1/hackrx/run"

def test_api():
    """Test the API without authentication"""
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "What are the coverage limits?",
            "What is the claim settlement process?",
            "What are the exclusions mentioned?"
        ]
    }

    print("🚀 Testing API")
    print(f"📡 Endpoint: {API_URL}")
    print("❓ Questions: 5 questions")
    print("-" * 60)
    
    try:
        print("⏱️  Starting API test...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            result = response.json()
            
            # Display results in a structured format
            print("\n" + "="*80)
            print("📋 QUERY RESULTS")
            print("="*80)
            
            answers = result.get('answers', [])
            questions = payload['questions']
            
            for i, (question, answer) in enumerate(zip(questions, answers), 1):
                print(f"\n� Question {i}:")
                print(f"   {question}")
                print(f"\n💡 Answer:")
                print(f"   {answer}")
                
                if i < len(questions):
                    print("\n" + "-"*60)
            
            print("\n" + "="*80)
            print(f"✨ Successfully processed {len(answers)} questions!")
            print("="*80)
            
            # Also print raw JSON for debugging
            print(f"\n🔧 Raw JSON Response:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API. Make sure the server is running.")
        print("💡 Start the server with: uvicorn app.main:app --reload")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_api()
