import re

def split_hebrew_word_to_letters(text: str) -> list[str]:
    letters = []
    word_start = True
    i = 0
    while i < len(text):
        sign = text[i]
        
        # Check for word breaks
        if sign in ['-', ' ', '\t', '\n'] or sign.isspace() or sign in ',.?!':
            word_start = True
            i += 1
            continue
            
        # Handle new letter or word start
        if word_start or not ('\u0591' <= sign <= '\u05C7'):
            letter_dict = {
                'letter': sign,
                'nikud': None,
                'is_dagesh': False,
                'shin': None,
                'is_heb': '\u05D0' <= sign <= '\u05EA'  # Hebrew letter range
            }
            letters.append(letter_dict)
            word_start = False
            
        # Handle diacritics
        else:
            if sign in ['\u05C1', '\u05C2']:  # Shin/Sin dots
                if letters[-1]['shin'] is None:
                    letters[-1]['shin'] = 'right' if sign == '\u05C1' else 'left'
            elif sign == '\u05BC':  # Dagesh
                if letters[-1]['letter'] == 'ו':
                    if letters[-1]['nikud'] is None:
                        letters[-1]['nikud'] = 'shuruk'
                else:
                    letters[-1]['is_dagesh'] = True
            else:  # Other nikud
                letters[-1]['nikud'] = sign
                
        i += 1
    return letters

def split_to_words(text: str) -> list[dict]:
    """
    Split text into words while preserving separators between them.
    
    Args:
        text: Hebrew text to split
        
    Returns:
        List of dictionaries with 'word' and 'separator' keys
    """
    words = []
    # Find all word boundaries including separators
    pattern = r'([\s\-\u05BE,.?!]+)'
    parts = re.split(pattern, text)
    
    # Process parts alternating between words and separators
    for i in range(0, len(parts), 2):
        word = parts[i]
        if word:  # Skip empty words
            separator = parts[i + 1] if i + 1 < len(parts) else ""
            words.append({
                'word': word,
                'separator': separator
            })
    
    return words

def split_to_words_and_letters(text: str) -> list[list[dict]]:
    """
    Split text into words and then split each word into letter dictionaries.
    
    Args:
        text: Hebrew text to split
        
    Returns:
        List of words, where each word is a list of letter dictionaries
    """
    words = split_to_words(text)
    words_with_letters = []
    
    for word in words:
        letters = split_hebrew_word_to_letters(word)
        words_with_letters.append(letters)
    
    return words_with_letters

def normalize_final_letters(text: str) -> str:
    """
    Normalize final letters based on position and dagesh.
    Final forms in non-final positions are converted to regular forms.
    In final positions: letters with dagesh become regular forms, others become final forms.
    """
    final_map = {"ך":"כ","ם":"מ","ן":"נ","ף":"פ","ץ":"צ"}
    reverse_final_map = {"כ":"ך","מ":"ם","נ":"ן","פ":"ף","צ":"ץ"}
    all_final_letters = set(final_map.keys()) | set(reverse_final_map.keys())
    
    words_with_letters = split_to_words_and_letters(text)
    result_words = []
    
    for word_letters in words_with_letters:
        for i, letter_dict in enumerate(word_letters):
            letter = letter_dict['letter']
            is_final_position = (i == len(word_letters) - 1)
            
            # If final form in non-final position, convert to regular form
            if letter in final_map and not is_final_position:
                letter_dict['letter'] = final_map[letter]
            
            # If final position
            elif is_final_position and letter in all_final_letters:
                if letter_dict['is_dagesh'] and letter in final_map:
                    # Has dagesh - keep regular form
                    letter_dict['letter'] = final_map[letter]
                elif letter in reverse_final_map:
                    # No dagesh - convert to final form
                    letter_dict['letter'] = reverse_final_map[letter]
        
        # Reconstruct word from letters
        word = ''.join(letter_dict['letter'] for letter_dict in word_letters)
        result_words.append(word)
    
    return ' '.join(result_words)

def normalize_full_ktiv(text: str) -> str:
    """
    Normalize full ktiv (final form) to regular form.
    
    This function implements the Hebrew text normalization rules for converting
    full ktiv (כתיב מלא) to regular form with proper vowel letter handling.
    
    Args:
        text: Hebrew text to normalize
        
    Returns:
        Normalized Hebrew text with proper vowel letter placement
    """
    # Import here to avoid circular imports
    from .nikud import add_nikud
    
    # Step 0: Add nikud using add_nikud with keep_vowels=False
    text_with_nikud = add_nikud(text, keep_vowels=False)
    
    # Step 1: Convert to words and letters
    words_with_letters = split_to_words_and_letters(text_with_nikud)
    result_words = []
    
    # Step 2: Walk through words
    for word_letters in words_with_letters:
        if not word_letters:
            continue
            
        # Step 3: Walk through letters
        i = 0
        while i < len(word_letters):
            current_letter = word_letters[i]
            current_nikud = current_letter.get('nikud')
            current_char = current_letter['letter']
            
            # Step 4: Handle kubutz (קובוץ) - add vav if next letter is not vav
            if current_nikud == '\u05BB':  # קובוץ
                if i + 1 < len(word_letters):
                    next_char = word_letters[i + 1]['letter']
                    if next_char != 'ו':
                        # Insert vav with kubutz after current letter
                        vav_letter = {
                            'letter': 'ו',
                            'nikud': '\u05BB',  # קובוץ
                            'is_dagesh': False,
                            'shin': None,
                            'is_heb': True
                        }
                        word_letters.insert(i + 1, vav_letter)
                        i += 1  # Skip the inserted vav in next iteration
            
            # Step 5: Handle holam (חולם) - add vav unless specific conditions
            elif current_nikud == '\u05B9':  # חולם
                if i + 1 < len(word_letters):
                    next_char = word_letters[i + 1]['letter']
                    next_nikud = word_letters[i + 1].get('nikud')
                    is_next_final = (i + 1 == len(word_letters) - 1)
                    
                    # Add vav unless next letter is ה without nikud, or א without nikud (not final)
                    should_add_vav = True
                    if next_char == 'ה' and next_nikud is None:
                        should_add_vav = False
                    elif next_char == 'א' and next_nikud is None and not is_next_final:
                        should_add_vav = False
                    
                    if should_add_vav:
                        # Insert vav with holam after current letter
                        vav_letter = {
                            'letter': 'ו',
                            'nikud': '\u05B9',  # חולם
                            'is_dagesh': False,
                            'shin': None,
                            'is_heb': True
                        }
                        word_letters.insert(i + 1, vav_letter)
                        i += 1  # Skip the inserted vav in next iteration
            
            # Step 6: Handle hirik (חיריק) - add yod if next nikud is not shva and not final
            elif current_nikud == '\u05B4':  # חיריק
                if i + 1 < len(word_letters):
                    next_nikud = word_letters[i + 1].get('nikud')
                    is_next_final = (i + 1 == len(word_letters) - 1)
                    
                    # Add yod if next nikud is not shva and not final letter
                    if next_nikud != '\u05B0' and not is_next_final:  # שווא
                        # Insert yod with hirik after current letter
                        yod_letter = {
                            'letter': 'י',
                            'nikud': '\u05B4',  # חיריק
                            'is_dagesh': False,
                            'shin': None,
                            'is_heb': True
                        }
                        word_letters.insert(i + 1, yod_letter)
                        i += 1  # Skip the inserted yod in next iteration
            
            # Step 7: Handle yod-vav doubling conditions
            elif current_char in ['י', 'ו']:
                # Check yod-vav doubling conditions
                is_first = (i == 0)
                is_last = (i == len(word_letters) - 1)
                
                if not is_first and not is_last:
                    prev_char = word_letters[i - 1]['letter']
                    prev_nikud = word_letters[i - 1].get('nikud')
                    next_char = word_letters[i + 1]['letter']
                    next_nikud = word_letters[i + 1].get('nikud')
                    
                    # Check if previous and next letters are not אהוי without nikud
                    prev_has_nikud = prev_nikud is not None
                    next_has_nikud = next_nikud is not None
                    
                    # If both previous and next have nikud (or are not אהוי), double the letter
                    if prev_has_nikud and next_has_nikud:
                        # Insert duplicate letter without nikud or dagesh
                        duplicate_letter = {
                            'letter': current_char,
                            'nikud': None,
                            'is_dagesh': False,
                            'shin': None,
                            'is_heb': True
                        }
                        word_letters.insert(i + 1, duplicate_letter)
                        i += 1  # Skip the inserted duplicate in next iteration
            
            i += 1
        
        # Reconstruct word from letters
        word = ''.join(letter_dict['letter'] for letter_dict in word_letters)
        result_words.append(word)
    
    return ' '.join(result_words)

def remove_nikud(text: str) -> str:
    """
    Remove all nikud marks from Hebrew text.
    
    Args:
        text: Hebrew text with nikud
        
    Returns:
        Hebrew text without nikud marks
    """
    # Remove nikud marks using Unicode range
    return re.sub(r'[\u0591-\u05C7]', '', text)

def normalize(text: str, with_nikud: bool=False, spellcheck: bool=False, customization=None) -> str:
    # Example: unify final letters
    text = normalize_final_letters(text)

    text = normalize_full_ktiv(text)
    
    # Remove nikud if not requested
    if not with_nikud:
        text = remove_nikud(text)

    return text.strip()
