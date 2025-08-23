import pathlib
from symspellpy import SymSpell
import re
import csv

class HebrewTokenizer:

    def normalize(self, text: str) -> str:
        """
        נרמול טקסט:
        - מסיר ניקוד
        - מאחד גרשיים/גרשים
        - מנרמל מקפים
        - מנקה רווחים מיותרים
        - לא מפרק מילים עם גרשיים/מרכאות
        """

        # הסרת ניקוד (טווח יוניקוד של ניקוד עברי)
        text = re.sub(r'[\u0591-\u05C7]', '', text)

        # אחידות גרשים
        text = re.sub(r"[`׳`‛‚ʻ’]", "'", text)   # גרש → '
        text = re.sub(r'[“”„‟«»]', '"', text)    # מירכאות → "

        # אחידות מקפים
        text = re.sub(r'[־‒–—―−]', ' ', text)

        # איחוד רווחים (אבל שומר על ירידות שורה)
        text = re.sub(r'[^\S\n]+', ' ', text)

        # ניקוי רווחים כפולים
        text = re.sub(r' +', ' ', text)

        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """
        פיצול לרשימת טוקנים (רק עברית).
        1. Split by whitespace
        2. If word doesn't start with heb letter א-ת, remove it
        3. If any letter is not a heb letter, remove it. Allow ' and "
        4. If the word contants a final letter ךםןףץ not in the final spot, but including ' - remove it
             so ץ' at the end is fine, but ץר is not
        5. All remaining words are valid hebrew words
        """
        
        # 1. Split by whitespace
        words = text.split()
        
        valid_tokens = []
        
        for word in words:
            # 2. If word doesn't start with heb letter א-ת, remove it
            if not word or not ('\u05D0' <= word[0] <= '\u05EA'):
                continue

            # 3. Check for final letters not in final position
            final_letters = {'ך', 'ם', 'ן', 'ף', 'ץ'}
            is_valid = True
            
            for i, char in enumerate(word):
                if not ('\u05D0' <= char <= '\u05EA' or (i>=1 and char in ["'", '"'])):
                    is_valid = False
                    break

                if char in final_letters:
                    # Check if this is the last character or followed by quote
                    if i == len(word) - 1:
                        # Final position - this is fine
                        continue
                    elif i == len(word) - 2 and word[i + 1] in ["'", '"']:
                        # Second to last with quote - this is fine (e.g., ץ')
                        continue
                    else:
                        # Final letter not in final position - invalid word
                        is_valid = False
                        break
            
            # 4. All remaining words are valid hebrew words
            if is_valid:
                valid_tokens.append(word)
        
        return valid_tokens


class CorpusLoader:
    def __init__(self, data_dir: str):
        self.data_dir = pathlib.Path(data_dir)

    def load_texts(self) -> list[str]:
        print("Loading texts from ", self.data_dir)
        texts = []
        for file in self.data_dir.glob("*.txt"):
            print(file)
            texts.append(file.read_text(encoding="utf-8"))
        return texts

    def load_tokens(self, tokenizer) -> list[str]:
        texts = self.load_texts()
        tokens = []
        for t in texts:
            norm = tokenizer.normalize(t)
            tokens.extend(tokenizer.tokenize(norm))
        return tokens

from collections import Counter

# עלויות החלפה מותאמות לעברית
CONFUSIONS = {
    ("א", "ע"): 0.5, ("ע", "א"): 0.5,
    ("כ", "ק"): 0.5, ("ק", "כ"): 0.5,
    ("ת", "ט"): 0.5, ("ט", "ת"): 0.5,
    ("ס", "ש"): 0.5, ("ש", "ס"): 0.5,
    ("ח", "כ"): 0.5, ("כ", "ח"): 0.5,
}

def weighted_levenshtein(a: str, b: str) -> float:
    """
    Levenshtein מותאם לעברית עם עלויות שונות להחלפות שכיחות.
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else CONFUSIONS.get((a[i - 1], b[j - 1]), 1)
            dp[i][j] = min(
                dp[i - 1][j] + 1,        # מחיקה
                dp[i][j - 1] + 1,        # הוספה
                dp[i - 1][j - 1] + cost  # החלפה
            )
    return dp[n][m]

def hebrew_rerank(symspell, word: str, top_k: int = 5):
    """
    משתמש ב-SymSpell כדי למצוא מועמדים ואז מדרג עם weighted levenshtein.
    """
    candidates = symspell.lookup(word, verbosity=2, max_edit_distance=2)
    print(candidates)
    for c in candidates:
        print(c.term,c.count)

    # Re-rank with weighted distance
    try:
        reranked_candidates = [{"term": c.term, "distance": weighted_levenshtein(word, c.term), "count": c.count} for c in candidates]
        print("reranked_candidates",reranked_candidates)
        ranked = sorted(
            reranked_candidates,
            key=lambda x: (x["distance"], -x["count"])  # קודם לפי מרחק מותאם, אח"כ לפי שכיחות
        )
    except Exception as e:
        print(21)
        print(e)

    print(3)

    print(ranked)
    return ranked[:top_k]


class SymSpellBuilder:
    def __init__(self, max_edit_distance, prefix_length):
        self.sym_spell = SymSpell(max_edit_distance, prefix_length)

    def build_from_tokens(self, tokens: list[str]):
        # ספירת תדירויות
        counts = Counter(tokens)
        for word, freq in counts.items():
            self.sym_spell.create_dictionary_entry(word, freq)

    def get_spellchecker(self):
        """Return the built SymSpell object"""
        return self.sym_spell

    def save_dictionary(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            for word, count in self.sym_spell.words.items():
                f.write(f"{word} {count}\n")

    def load(self, filepath):
        self.sym_spell.load_dictionary(filepath, 0, 1)

class SpellChecker:
    def __init__(self, symspell, tokenizer):
        self.symspell = symspell
        self.tokenizer = tokenizer

    def correct_word(self, word: str) -> str:
        print(self,word)
        suggestions = hebrew_rerank(self.symspell, word)
        print(2)
        if suggestions:
            print(suggestions)
            return suggestions[0]['term']
        return word

    def correct_text(self, text: str) -> str:
        norm = self.tokenizer.normalize(text)
        tokens = self.tokenizer.tokenize(norm)
        corrected_tokens = [self.correct_word(t) for t in tokens]
        return " ".join(corrected_tokens)


def spellchecker_test(spellchecker, filename: str):
    """
    Test the spellchecker against a CSV file with form and correct columns.
    
    Args:
        spellchecker: SpellChecker instance to test
        filename: Path to CSV file with 'form' and 'correct' columns
        
    Returns:
        Dictionary with test statistics
    """
    print(f"🧪 Testing spellchecker against {filename}")
    print("=" * 60)
    
    # Statistics tracking
    total_words = 0
    correctly_corrected = 0
    incorrectly_corrected = 0
    not_corrected = 0
    
    # Track incorrect corrections for display
    incorrect_corrections = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Verify required columns exist
            if 'form' not in reader.fieldnames or 'correct' not in reader.fieldnames:
                print(f"❌ Error: CSV must have 'form' and 'correct' columns. Found: {reader.fieldnames}")
                return None
            
            print(f"📊 CSV columns: {reader.fieldnames}")
            print()
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 because row 1 is header
                form = row['form'].strip()
                correct = row['correct'].strip()
                
                if not form or not correct:
                    continue
                
                total_words += 1
                
                # Get spellchecker correction
                corrected = spellchecker.correct_word(form)
                
                # Check if correction is correct
                if corrected == correct:
                    correctly_corrected += 1
                    print(f"   ✅ Row {row_num}: '{form}' → '{corrected}' (correct)")
                elif corrected == form:
                    not_corrected += 1
                    print(f"   ⚠️  Row {row_num}: '{form}' → '{corrected}' (not corrected)")
                else:
                    incorrectly_corrected += 1
                    print(f"   ❌ Row {row_num}: '{form}' → '{corrected}' (expected: '{correct}')")
                    
                    # Store for summary
                    incorrect_corrections.append({
                        'row': row_num,
                        'form': form,
                        'corrected': corrected,
                        'expected': correct
                    })
    
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        return None
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None
    
    # Calculate statistics
    if total_words == 0:
        print("❌ No valid words found in CSV file")
        return None
    
    accuracy_percentage = (correctly_corrected / total_words) * 100
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 SPELLCHECKER TEST RESULTS")
    print("=" * 60)
    print(f"Total words tested: {total_words}")
    print(f"Correctly corrected: {correctly_corrected}")
    print(f"Incorrectly corrected: {incorrectly_corrected}")
    print(f"Not corrected: {not_corrected}")
    print(f"Accuracy: {accuracy_percentage:.2f}%")
    
    # Display incorrect corrections summary
    if incorrect_corrections:
        print(f"\n❌ INCORRECT CORRECTIONS ({len(incorrect_corrections)}):")
        print("-" * 40)
        for item in incorrect_corrections[:10]:  # Show first 10
            print(f"Row {item['row']}: '{item['form']}' → '{item['corrected']}' (expected: '{item['expected']}')")
        
        if len(incorrect_corrections) > 10:
            print(f"... and {len(incorrect_corrections) - 10} more")
    
    # Return statistics
    stats = {
        'total_words': total_words,
        'correctly_corrected': correctly_corrected,
        'incorrectly_corrected': incorrectly_corrected,
        'not_corrected': not_corrected,
        'accuracy_percentage': accuracy_percentage,
        'incorrect_corrections': incorrect_corrections
    }
    
    return stats

def builder_spellcheck():
    """
    Build spellchecker from corpus.
    This function requires the app to be running or proper environment setup.
    """
    try:
        # Try to import from app config
        from app.config import settings
        loader = CorpusLoader(settings.spellchecker_corpus_dir)    
    except ImportError:
        # Fallback for when running standalone
        print("⚠️  Warning: Could not import app.config. Using default values.")
        # Use default values for standalone testing
        loader = CorpusLoader("./data/corpus")  # Default path
    
    try:
        # 1. טוקניזציה
        tokenizer = HebrewTokenizer()

        # 2. Load corpus
        tokens = loader.load_tokens(tokenizer)

        # 3. Build dictionary
        builder = SymSpellBuilder(2, 7)  # Default values
        builder.build_from_tokens(tokens)

        builder.save_dictionary("app/data/symspell/symspell.txt")

        #builder.load("app/data/symspell/symspell.txt")

        # 4. Create spellchecker
        spellchecker = SpellChecker(builder.get_spellchecker(), tokenizer)

        print("✅ Spellchecker built successfully!")
        print(f"Sample correction: 'ראיון' → '{spellchecker.correct_word('ראיון')}'")
        print(f"Sample correction: 'ראיוש' → '{spellchecker.correct_word('ראיוש')}'")
        
        # Example of how to test the spellchecker
        print("\n💡 To test the spellchecker with a CSV file:")
        print("   stats = spellchecker_test(spellchecker, 'test_data.csv')")
        print("   # CSV should have columns: form,correct")
        print("   # Example CSV content:")
        print("   # form,correct")
        print("   # ראיון,ראיון")
        print("   # ראיוש,ראיון")
        print("   # עובדים,עובדים")
        
        return spellchecker
        
    except Exception as e:
        print(f"❌ Error building spellchecker: {e}")
        print("💡 Make sure you have a corpus directory with .txt files")
        return None


def spellcheck(text: str) -> str:
    """
    Basic spellcheck function that can work without external dependencies.
    
    Args:
        text: Hebrew text to spellcheck
        
    Returns:
        Spellchecked text (currently a placeholder)
    """
    # Placeholder — future: AlephBERT / HSpell
    return text + " [spellchecked]"


# Only run if this file is executed directly
if __name__ == "__main__":
    print("🔤 Building Hebrew Spellchecker...")
    print("=" * 40)
    
    # Try to build the spellchecker
    spellchecker = builder_spellcheck()

    test_filename = "app/data/spellcheck_test/spelling_errors.csv"
    stats = spellchecker_test(spellchecker, test_filename)
    print(stats)
    
    if spellchecker:
        print("\n🎉 Spellchecker is ready!")
        print("💡 You can now use it in your application")
    else:
        print("\n⚠️  Spellchecker build failed")
        print("💡 Check the error messages above")