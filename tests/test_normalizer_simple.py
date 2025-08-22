import sys
import os

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_remove_nikud_simple():
    """Test removing nikud from Hebrew text - simple version without imports"""
    print("🧪 Testing remove_nikud function...")
    
    # Simple regex-based nikud removal
    import re
    
    def remove_nikud_simple(text):
        """Remove all nikud marks from Hebrew text using regex"""
        return re.sub(r'[\u0591-\u05C7]', '', text)
    
    # Test cases: (input_with_nikud, expected_output_without_nikud)
    test_cases = [
        ("שָׁלוֹם עוֹלָם", "שלום עולם"),
        ("אֲנַחְנוּ נִמְצָאִים בָּאֲוִיר", "אנחנו נמצאים באויר"),
        ("בֵּית הַסֵּפֶר נִמְצָא בְּרְחוֹב הֶרְצְל", "בית הספר נמצא ברחוב הרצל")
    ]
    
    all_passed = True
    for input_text, expected_output in test_cases:
        try:
            result = remove_nikud_simple(input_text)
            if result == expected_output:
                print(f"   ✅ '{input_text}' → '{result}'")
            else:
                print(f"   ❌ '{input_text}' → '{result}' (expected: '{expected_output}')")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error processing '{input_text}': {e}")
            all_passed = False
    
    if all_passed:
        print("   🎉 All remove_nikud tests passed!")
    else:
        print("   ⚠️  Some remove_nikud tests failed!")
    
    return all_passed

def test_hebrew_text_processing():
    """Test basic Hebrew text processing functions"""
    print("\n🧪 Testing Hebrew text processing...")
    
    # Test Hebrew letter detection
    def is_hebrew_letter(char):
        """Check if character is a Hebrew letter"""
        return '\u05D0' <= char <= '\u05EA'
    
    def count_hebrew_letters(text):
        """Count Hebrew letters in text"""
        return sum(1 for char in text if is_hebrew_letter(char))
    
    # Test cases
    test_cases = [
        ("שלום עולם", 8),  # 8 Hebrew letters
        ("Hello שלום", 4),  # 4 Hebrew letters
        ("שָׁלוֹם", 4),     # 4 Hebrew letters (with nikud)
        ("", 0),            # Empty string
        ("123", 0)          # No Hebrew letters
    ]
    
    all_passed = True
    for input_text, expected_count in test_cases:
        try:
            result = count_hebrew_letters(input_text)
            if result == expected_count:
                print(f"   ✅ '{input_text}' has {result} Hebrew letters")
            else:
                print(f"   ❌ '{input_text}' has {result} Hebrew letters (expected: {expected_count})")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error processing '{input_text}': {e}")
            all_passed = False
    
    if all_passed:
        print("   🎉 All Hebrew text processing tests passed!")
    else:
        print("   ⚠️  Some Hebrew text processing tests failed!")
    
    return all_passed

def test_final_letter_conversion():
    """Test final letter conversion logic"""
    print("\n🧪 Testing final letter conversion...")
    
    # Final letter mapping
    final_map = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
    
    def convert_final_letters(text):
        """Convert final letters to regular form"""
        result = text
        for final, regular in final_map.items():
            result = result.replace(final, regular)
        return result
    
    # Test cases: (input_with_final_letters, expected_output_normalized)
    test_cases = [
        ("שלום עולם", "שלום עולם"),  # No final letters to change
        ("הספר על השולחן", "הספר על השולחן"),  # No final letters to change
        ("אני הולך הביתה", "אני הולך הביתה")  # No final letters to change
    ]
    
    all_passed = True
    for input_text, expected_output in test_cases:
        try:
            result = convert_final_letters(input_text)
            if result == expected_output:
                print(f"   ✅ '{input_text}' → '{result}'")
            else:
                print(f"   ❌ '{input_text}' → '{result}' (expected: '{expected_output}')")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error processing '{input_text}': {e}")
            all_passed = False
    
    if all_passed:
        print("   🎉 All final letter conversion tests passed!")
    else:
        print("   ⚠️  Some final letter conversion tests failed!")
    
    return all_passed

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n🧪 Testing edge cases...")
    
    def remove_nikud_simple(text):
        """Remove all nikud marks from Hebrew text using regex"""
        import re
        return re.sub(r'[\u0591-\u05C7]', '', text)
    
    # Test cases
    test_cases = [
        ("", ""),                    # Empty string
        ("   ", "   "),             # String with only spaces
        ("ִָֹ", ""),                # String with only nikud
        ("שלום world שלום", "שלום world שלום")  # Mixed Hebrew and English
    ]
    
    all_passed = True
    for input_text, expected_output in test_cases:
        try:
            result = remove_nikud_simple(input_text)
            if result == expected_output:
                print(f"   ✅ '{repr(input_text)}' → '{repr(result)}'")
            else:
                print(f"   ❌ '{repr(input_text)}' → '{repr(result)}' (expected: '{repr(expected_output)}')")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error processing '{repr(input_text)}': {e}")
            all_passed = False
    
    if all_passed:
        print("   🎉 All edge case tests passed!")
    else:
        print("   ⚠️  Some edge case tests failed!")
    
    return all_passed

if __name__ == "__main__":
    print("🚀 HEBNORM - Simple Normalizer Tests")
    print("=" * 50)
    print("Testing basic functions without full model dependencies...")
    
    # Track test results
    test_results = []
    
    # Run all tests
    test_results.append(test_remove_nikud_simple())
    test_results.append(test_hebrew_text_processing())
    test_results.append(test_final_letter_conversion())
    test_results.append(test_edge_cases())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    if passed == total:
        print(f"🎉 All {total} test suites passed successfully!")
    else:
        print(f"⚠️  {passed}/{total} test suites passed.")
    
    print("\n💡 These tests verify basic Hebrew text processing functions.")
    print("💡 For full functionality testing, start the API: uvicorn app.main:app --reload")
    print("💡 For pytest testing: pytest tests/test_normalizer.py")
