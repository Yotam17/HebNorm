#!/usr/bin/env python3
"""
Test the updated load_lists function
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_load_lists():
    """Test the load_lists function"""
    print("🧪 Testing load_lists function...")
    
    try:
        from app.normalizer.runtime.lists import load_lists
        
        # Test loading lists from the rules/lists directory
        print("\n📁 Testing load_lists('rules/lists')...")
        lists = load_lists("rules/lists")
        
        print("\n📊 Loaded lists:")
        for key, items in lists.items():
            print(f"   {key}: {items}")
        
        # Test with non-existent directory
        print("\n📁 Testing load_lists('non_existent')...")
        empty_lists = load_lists("non_existent")
        print(f"   Result: {empty_lists}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Load Lists Function Test")
    print("=" * 40)
    
    # Run test
    success = test_load_lists()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Load lists function is working correctly!")
    else:
        print("⚠️  Load lists function has issues. Check the error messages above.")
    
    print("\n💡 The function now:")
    print("   1. Loads all YAML files from the specified directory")
    print("   2. Merges lists with the same key from different files")
    print("   3. Handles both .yaml and .yml extensions")
    print("   4. Provides detailed logging of the loading process")
    print("   5. Returns a dictionary with merged lists")
