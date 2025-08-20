#!/usr/bin/env python3
"""
Simple test to check if imports work
"""

try:
    print("Testing imports...")
    
    # Test config import
    from app.config import settings
    print("✅ Config import successful")
    print(f"   Model: {settings.nikud_model}")
    
    # Test main app import
    from app.main import app
    print("✅ Main app import successful")
    
    print("\n🎉 All imports successful!")
    print("The project is ready to run!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTo fix this, install dependencies:")
    print("pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

def test_normalize_full_ktiv():
    """Test the normalize_full_ktiv function"""
    from app.utils.normalizer import normalize_full_ktiv
    
    print("🔤 Normalize Full Ktiv Test:")
    
    # Test cases for full ktiv normalization
    test_cases = [
        "שלום עולם",  # Basic test
        "אנחנו נמצאים באויר",  # Test with various nikud
        "בית הספר נמצא ברחוב הרצל"  # Test with final letters
    ]
    
    for text in test_cases:
        try:
            result = normalize_full_ktiv(text)
            print(f"   Input:  {text}")
            print(f"   Output: {result}")
            print()
        except Exception as e:
            print(f"   Error for '{text}': {e}")
            print()

if __name__ == "__main__":
    print("🚀 HEBNORM - Hebrew Text Normalizer API")
    print("=" * 50)
    
    # Test basic imports
    test_imports()
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test normalize_full_ktiv function
    test_normalize_full_ktiv()
    
    print("✅ All tests completed!")
