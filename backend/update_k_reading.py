import json
import sys
import os

# Add backend directory to sys.path to import lyrics_processor
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from lyrics_processor import furitohan_str

file_path = os.path.join(os.path.dirname(__file__), 'japanese_words_1.json')

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

updated_count = 0

for item in data:
    reading = item.get('reading', '')
    if reading:
        # furitohan_str converts hiragana to korean pronunciation
        new_k_reading = furitohan_str(reading)
        if item.get('k_reading') != new_k_reading:
            item['k_reading'] = new_k_reading
            updated_count += 1

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Update complete. {updated_count} items updated.")
