#!/usr/bin/env python3
"""
HEBNORM API Usage Examples
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("🏠 Root Endpoint:")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Name: {data.get('name', 'N/A')}")
        print(f"   Version: {data.get('version', 'N/A')}")
        print(f"   API Version: {data.get('api_version', 'N/A')}")
        print()
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        print("   Run: uvicorn app.main:app --reload")
        print()
        return False

def test_healthcheck():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("🏥 Health Check:")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Health: {data.get('status', 'N/A')}")
        print(f"   Model: {data.get('model', 'N/A')}")
        if 'system' in data:
            print(f"   Platform: {data['system'].get('platform', 'N/A')}")
        if 'memory' in data:
            print(f"   Memory Used: {data['memory'].get('percent_used', 'N/A')}%")
        print()
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("   ❌ API not available")
        return False

def test_add_nikud():
    """Test the add_nikud endpoint"""
    test_cases = [
        {"text": "שלום עולם", "keep_vowels": False},
        {"text": "אנחנו נמצאים באויר", "keep_vowels": True},
        {"text": "בית הספר נמצא ברחוב הרצל", "keep_vowels": False}
    ]
    
    print("🔤 Add Nikud Examples:")
    for case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/add_nikud",
                json=case
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   Input:  {result['input']}")
                print(f"   Output: {result['output']}")
                print(f"   Keep Vowels: {result.get('keep_vowels', 'N/A')}")
                print()
            else:
                print(f"   Error for '{case['text']}': {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ API not available")
            break

def test_normalize():
    """Test the normalize endpoint"""
    test_cases = [
        {"text": "אנחנו נמצאימ באויר", "with_nikud": False, "spellcheck": True},
        {"text": "הבית נמצא ברחוב הרצל", "with_nikud": True, "spellcheck": False},
        {"text": "שלום עולם", "with_nikud": False, "spellcheck": False}
    ]
    
    print("📝 Normalize Examples:")
    for case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/normalize",
                json=case
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   Input:  {result['input']}")
                print(f"   Output: {result['output']}")
                print(f"   Options: nikud={case['with_nikud']}, spellcheck={case['spellcheck']}")
                print()
            else:
                print(f"   Error for '{case['text']}': {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ API not available")
            break

def test_spellcheck():
    """Test the spellcheck endpoint"""
    texts = [
        "שלום עולם",
        "אנחנו נמצאים באויר",
        "בית הספר נמצא ברחוב הרצל"
    ]
    
    print("✅ Spellcheck Examples:")
    for text in texts:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/spellcheck",
                json={"text": text}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   Input:  {result['input']}")
                print(f"   Output: {result['output']}")
                print()
            else:
                print(f"   Error for '{text}': {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ API not available")
            break

def test_normalize_full_ktiv():
    """Test the normalize_full_ktiv function"""
    print("🔤 Normalize Full Ktiv Examples:")
    
    # Test cases for full ktiv normalization
    test_cases = [
        "שלום עולם",
        "אנחנו נמצאים באויר", 
        "בית הספר נמצא ברחוב הרצל"
    ]
    
    for text in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/normalize",
                json={"text": text, "with_nikud": True}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   Input:  {result['input']}")
                print(f"   Output: {result['output']}")
                print()
            else:
                print(f"   Error for '{text}': {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ API not available")

def main():
    """Run all examples"""
    print("🎯 HEBNORM API Examples")
    print("=" * 50)
    print()
    
    # Test root endpoint first
    if not test_root():
        return
    
    # Test health check
    if not test_healthcheck():
        return
    
    # Test all endpoints
    test_add_nikud()
    test_normalize()
    test_spellcheck()
    test_normalize_full_ktiv()
    
    print("🎉 All examples completed!")
    print()
    print("💡 Tips:")
    print("   - Use different Hebrew texts to test")
    print("   - Try various normalization options")
    print("   - Check the API documentation at http://localhost:8000/docs")
    print("   - API v1 endpoints are available at /api/v1/*")

if __name__ == "__main__":
    print("🚀 HEBNORM - Hebrew Text Normalizer API Examples")
    print("=" * 60)
    
    # Test root endpoint
    test_root()
    
    # Test health check
    test_healthcheck()
    
    # Test add nikud endpoint
    test_add_nikud()
    
    # Test normalize endpoint
    test_normalize()
    
    # Test spellcheck endpoint
    test_spellcheck()
    
    # Test normalize_full_ktiv functionality
    test_normalize_full_ktiv()
    
    print("✅ All examples completed!")
