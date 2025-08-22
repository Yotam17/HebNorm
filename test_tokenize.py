#!/usr/bin/env python3
"""
Test the tokenize function from spellcheck.py
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_tokenize():
    """Test the tokenize function with various Hebrew text examples"""
    print("🧪 Testing tokenize function...")
    
    try:
        from app.utils.spellcheck import HebrewTokenizer
        
        tokenizer = HebrewTokenizer()
        
        # Test cases
        test_cases = [
            # Basic Hebrew text
            ("שלום עולם", ["שלום", "עולם"]),
            
            # Text with final letters in correct positions
            ("אני הולך הביתה", ["אני", "הולך", "הביתה"]),
            
            # Text with final letters and quotes
            ("הספר על השולחן", ["הספר", "על", "השולחן"]),
            
            # Text with mixed Hebrew and non-Hebrew
            ("שלום world שלום", ["שלום", "שלום"]),
            
            # Text with final letters in wrong positions (should be filtered out)
            ("שלום ץר עולם", ["שלום", "עולם"]),
            
            # Text with final letters and quotes in correct positions
            ("שלום ץ' עולם", ["שלום", "ץ'", "עולם"]),
            
            # Text with final letters at the end (should be kept)
            ("שלום ץ עולם", ["שלום", "ץ", "עולם"]),
            
            # Empty text
            ("", []),
            
            # Whitespace only
            ("   ", []),
            
            # Text starting with non-Hebrew
            ("123 שלום עולם", ["שלום", "עולם"]),
            
            # Text with multiple spaces
            ("שלום    עולם", ["שלום", "עולם"]),
        ]
        
        all_passed = True
        
        for input_text, expected_output in test_cases:
            try:
                result = tokenizer.tokenize(input_text)
                if result == expected_output:
                    print(f"   ✅ '{input_text}' → {result}")
                else:
                    print(f"   ❌ '{input_text}' → {result} (expected: {expected_output})")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ Error processing '{input_text}': {e}")
                all_passed = False
        
        if all_passed:
            print("   🎉 All tokenize tests passed!")
        else:
            print("   ⚠️  Some tokenize tests failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Tokenize Function Test")
    print("=" * 40)
    
    # Run test
    success = test_tokenize()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Tokenize function is working correctly!")
    else:
        print("⚠️  Tokenize function has issues. Check the error messages above.")
    
    print("\n💡 The tokenize function now implements all the rules:")
    print("   1. Split by whitespace")
    print("   2. Filter words that don't start with Hebrew letters")
    print("   3. Filter words with final letters in wrong positions")
    print("   4. Keep only valid Hebrew words")
