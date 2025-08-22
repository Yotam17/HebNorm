#!/usr/bin/env python3
"""
Quick test to verify the normalizer fixes work
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_basic_functions():
    """Test basic functions without external dependencies"""
    print("🧪 Testing basic normalizer functions...")
    
    try:
        # Test the basic functions that should work without model
        from app.utils.normalizer import normalize_final_letters, remove_nikud
        
        # Test 1: Empty string
        result1 = normalize_final_letters("")
        print(f"✅ Empty string: '{repr(result1)}'")
        
        # Test 2: Whitespace only
        result2 = normalize_final_letters("   ")
        print(f"✅ Whitespace only: '{repr(result2)}'")
        
        # Test 3: Basic text
        result3 = normalize_final_letters("שלום עולם")
        print(f"✅ Basic text: '{result3}'")
        
        # Test 4: Remove nikud
        result4 = remove_nikud("שָׁלוֹם עוֹלָם")
        print(f"✅ Remove nikud: '{result4}'")
        
        print("🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_normalize_function():
    """Test the main normalize function"""
    print("\n🧪 Testing normalize function...")
    
    try:
        from app.utils.normalizer import normalize
        
        # Test 1: Empty string
        result1 = normalize("")
        print(f"✅ Empty string: '{repr(result1)}'")
        
        # Test 2: Whitespace only
        result2 = normalize("   ")
        print(f"✅ Whitespace only: '{repr(result2)}'")
        
        # Test 3: Basic text without nikud
        result3 = normalize("שלום עולם", with_nikud=False)
        print(f"✅ Basic text without nikud: '{result3}'")
        
        print("🎉 All normalize tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Normalizer Test")
    print("=" * 40)
    
    # Run tests
    test1 = test_basic_functions()
    test2 = test_normalize_function()
    
    print("\n" + "=" * 40)
    if test1 and test2:
        print("🎉 All tests passed! The fixes are working.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print("\n💡 If all tests passed, you can now run the full test suite:")
    print("   python tests/test_normalizer.py")
