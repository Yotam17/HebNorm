import pathlib
from symspellpy import SymSpell, Verbosity
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


import pathlib

class CorpusLoader:
    def __init__(self, data_dir: str):
        self.data_dir = pathlib.Path(data_dir)

    def load_texts(self):
        """Generator – מחזיר שורות טקסט מכל הקבצים בהדרגה"""
        print("Streaming texts from", self.data_dir)

        for file in self.data_dir.glob("*.txt"):
            print(file)
            with file.open(encoding="utf-8") as f:
                for line in f:
                    yield line.strip()

        for file in self.data_dir.glob("*.csv"):
            print(file)
            with file.open(encoding="utf-8") as f:
                for line in f:
                    yield line.strip()

    def load_tokens(self, tokenizer):
        """Generator – מנרמל ומחזיר טוקנים בהדרגה"""
        # Global counter for progress tracking
        global line_counter
        line_counter = 0
        
        for text in self.load_texts():
            line_counter += 1
            
            # Display progress every 100,000 lines
            if line_counter % 100000 == 0:
                print(f"📊 Processed {line_counter:,} lines...")
                
            norm = tokenizer.normalize(text)
            for tok in tokenizer.tokenize(norm):
                yield tok

from collections import Counter

# עלויות החלפה מותאמות לעברית
CONFUSIONS = {
    ("א", "ע"): 0.3, ("ע", "א"): 0.3,
    ("א", "ה"): 0.3, ("ה", "א"): 0.3,
    ("ה", "ע"): 0.7, ("ע", "ה"): 0.7,
    ("ב", "ו"): 0.8, ("ו", "ב"): 0.8,
    ("כ", "ק"): 0.3, ("ק", "כ"): 0.3,
    ("ת", "ט"): 0.3, ("ט", "ת"): 0.3,
    ("ס", "ש"): 0.5, ("ש", "ס"): 0.5,
    ("ח", "כ"): 0.5, ("כ", "ח"): 0.5,
    ("ם", "ן"): 0.7, ("ן", "ם"): 0.7,
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
    # חובה להשתמש ב-Verbosity.ALL כדי לקבל את כל המועמדים
    candidates = symspell.lookup(word, verbosity=Verbosity.ALL, max_edit_distance=2)

    print(f"      🔍 All suggestions for '{word}':")
    for i, suggestion in enumerate(candidates[:top_k], 1):  # Show top 5
        distance = suggestion.distance
        count = suggestion.count
        term = suggestion.term
        print(f"         {i}. '{term}' (distance: {distance}, frequency: {count})")


    reranked_candidates = [
        {
            "term": c.term,
            "distance": weighted_levenshtein(word, c.term),
            "count": c.count,
        }
        for c in candidates
    ]

    ranked = sorted(
        reranked_candidates,
        key=lambda x: (x["distance"], -x["count"])  # קודם לפי מרחק מותאם, אח"כ לפי שכיחות
    )

    return ranked[:top_k]


from itertools import islice
from typing import Iterable, List

class SymSpellBuilder:
    """
    Build SymSpell dictionary efficiently:
    1) accumulate counts in-memory via Counter (chunked)
    2) prune by min_freq
    3) load into SymSpell (with tuned params)
    """

    def __init__(self, max_edit_distance: int = 1, prefix_length: int = 5) -> None:
        # עדיף שמות פרמטרים מפורשים (אבל גם positional עובד)
        self.sym_spell = SymSpell(
            max_dictionary_edit_distance=max_edit_distance,
            prefix_length=prefix_length,
        )
        self.max_edit_distance = max_edit_distance
        self.prefix_length = prefix_length

    # ---------- helpers ----------

    @staticmethod
    def chunked(iterable: Iterable[str], size: int) -> Iterable[List[str]]:
        """Yield lists of size `size` from iterable (last may be smaller)."""
        it = iter(iterable)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                break
            yield chunk

    @staticmethod
    def build_counts_from_stream(tokens: Iterable[str], chunk_size: int = 1_000_000, max_chunks: int = 10000) -> Counter:
        """Accumulate token frequencies into a single Counter by chunks."""
        print("Building counts from stream...")
        counts = Counter()
        for i,chunk in enumerate(SymSpellBuilder.chunked(tokens, chunk_size)):
            if i > max_chunks:
                break
            # Progress update every 5 chunks to avoid spam
            if i % 5 == 0:
                print(f"Processing chunk {i}/{max_chunks} (size: {len(chunk):,})")
            counts.update(chunk)
        print("Finished building counts from stream")
        return counts

    @staticmethod
    def prune_counts(counts: Counter, min_freq: int) -> List[tuple[str, int]]:
        """Filter rare tokens after full accumulation."""
        if min_freq <= 1:
            return list(counts.items())
        return [(w, c) for w, c in counts.items() if c >= min_freq]

    # ---------- main API ----------

    def build_symspell_from_counts(self, items: List[tuple[str, int]]) -> None:
        """Populate self.sym_spell from (word, freq) pairs."""
        for word, freq in items:
            # ב־symspellpy זה מצטבר אם המילה כבר קיימת
            self.sym_spell.create_dictionary_entry(word, freq)

    def build_from_tokens(
        self,
        tokens: Iterable[str],
        flush_every: int = 10_000_000,
        min_freq: int = 1,
    ) -> None:
        """Full pipeline: counts -> prune -> symspell."""
        counts = self.build_counts_from_stream(tokens, chunk_size=flush_every, max_chunks=10000)
        items = self.prune_counts(counts, min_freq=min_freq)
        self.build_symspell_from_counts(items)

    def get_spellchecker(self) -> SymSpell:
        """Return the built SymSpell object."""
        return self.sym_spell

    # ---------- I/O ----------
    def save_dictionary(self, filepath: str) -> None:
        """
        Save as 'term count' (space-separated), compatible with
        sym_spell.load_dictionary(..., term_index=0, count_index=1).
        """
        with open(filepath, "w", encoding="utf-8") as f:
            for term, val in self.sym_spell.words.items():
                # val הוא בדרך כלל int; אם זו גירסה/פורק עם אובייקטים, ננסה .count
                if isinstance(val, int):
                    freq = val
                elif hasattr(val, "count"):
                    freq = int(val.count)
                elif isinstance(val, (list, tuple)) and val and isinstance(val[0], int):
                    # גיבוי נדיר אם נשמר כמבנה אחר
                    freq = val[0]
                else:
                    raise TypeError(f"Unsupported value type for term {term!r}: {type(val)}")
                f.write(f"{term} {freq}\n")

    def load(self, filepath: str, term_index: int = 0, count_index: int = 1, separator: str = " ") -> None:
        # אתחול נקי על בסיס הערכים ששמרנו
        self.sym_spell = SymSpell(max_dictionary_edit_distance=self.max_edit_distance,
                                prefix_length=self.prefix_length)

        ok = self.sym_spell.load_dictionary(filepath, term_index, count_index, separator)
        if not ok:
            raise FileNotFoundError(f"Could not load dictionary from {filepath}")

class SpellChecker:
    def __init__(self, symspell, tokenizer):
        self.symspell = symspell
        self.tokenizer = tokenizer

    def correct_word(self, word: str, top_k: int = 1000) -> str:
        suggestions = hebrew_rerank(self.symspell, word, top_k)
        if suggestions:
            return suggestions[0]['term'],suggestions
        return word,[]

    def correct_text(self, text: str) -> str:
        norm = self.tokenizer.normalize(text)
        tokens = self.tokenizer.tokenize(norm)
        corrected_tokens = [self.correct_word(t)[0] for t in tokens]
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
                corrected,suggestions = spellchecker.correct_word(form)

                # Check if correction is correct
                if corrected == correct:
                    correctly_corrected += 1
                    #print(f"   ✅ Row {row_num}: '{form}' → '{corrected}' (correct)")
                elif corrected == form:
                    not_corrected += 1
                    print(f"   ⚠️  Row {row_num}: '{form}' → '{corrected}' (not corrected)")
                else:
                    incorrectly_corrected += 1
                    print(f"   ❌ Row {row_num}: '{form}' → '{corrected}' (expected: '{correct}'), suggestions: {suggestions}")
                    
                    # Print formatted suggestions for debugging
                    if suggestions:
                        print(f"      🔍 All suggestions for '{form}':")
                        for i, suggestion in enumerate(suggestions[:5], 1):  # Show top 5
                            distance = suggestion.get('distance', 'N/A')
                            count = suggestion.get('count', 'N/A')
                            term = suggestion.get('term', 'N/A')
                            print(f"         {i}. '{term}' (distance: {distance}, frequency: {count})")
                    else:
                        print(f"      🔍 No suggestions found for '{form}'")
                    
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

def builder_spellcheck(load_from_file: bool = True):
    """
    Build spellchecker from corpus.
    This function requires the app to be running or proper environment setup.
    """
    try:
        # Try to import from app config
        from app.config import settings
        print("settings",settings)
        loader = CorpusLoader(settings.spellchecker_corpus_dir)    
    except ImportError:
        # Fallback for when running standalone
        print("⚠️  Warning: Could not import app.config. Using default values.")
        # Use default values for standalone testing
        exit(1)
    
    try:
        # 1. טוקניזציה
        tokenizer = HebrewTokenizer()
        builder = SymSpellBuilder(2, 7)  # Default values

        if load_from_file:
            builder.load("app/data/symspell/symspell.txt")
            print(f"Loaded dictionary with {len(builder.sym_spell.words):,} words")
        else:
            # 2. Load corpus
            tokens = loader.load_tokens(tokenizer)
            # 3. Build dictionary
            builder.build_from_tokens(tokens, flush_every=10000000, min_freq=5)
            builder.save_dictionary("app/data/symspell/symspell.txt")

        # 4. Create spellchecker
        spellchecker = SpellChecker(builder.get_spellchecker(), tokenizer)

    
        print("✅ Spellchecker built successfully!")
        
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
    spellchecker = builder_spellcheck(load_from_file=True)

    test_filename = "app/data/spellcheck_test/spelling_errors2.csv"
    stats = spellchecker_test(spellchecker, test_filename)
    print(stats)
    
    if spellchecker:
        print("\n🎉 Spellchecker is ready!")
        print("💡 You can now use it in your application")
    else:
        print("\n⚠️  Spellchecker build failed")
        print("💡 Check the error messages above")