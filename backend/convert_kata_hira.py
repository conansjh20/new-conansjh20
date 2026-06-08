import json
import re

def is_katakana(text):
    # Match strings that consist entirely of Katakana block characters
    return bool(re.fullmatch(r'[\u30A0-\u30FF]+', text))

def katakana_to_hiragana(text):
    result = ""
    for char in text:
        code = ord(char)
        # Standard Katakana range to convert to Hiragana
        if 0x30A1 <= code <= 0x30F6:
            result += chr(code - 0x60)
        # For 'ヴ' (30F4) to 'ゔ' (3094), it works too.
        # Other characters like 'ー' (30FC) remain unchanged
        else:
            result += char
    return result

file_path = 'c:/coding/New_conansjh20.com/backend/japanese_words_1.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

converted_count = 0

for item in data:
    word = item.get('word', '')
    if is_katakana(word):
        new_reading = katakana_to_hiragana(word)
        if item.get('reading') != new_reading:
            item['reading'] = new_reading
            converted_count += 1

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Conversion complete. Updated {converted_count} items.")
