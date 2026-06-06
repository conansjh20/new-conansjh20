import json
import os
import sys
import jaconv

# Add backend directory to sys.path to import lyrics_processor
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_dir)

from lyrics_processor import furitohan_str

def update_json():
    filepath = os.path.join(backend_dir, 'japanese_words_1.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for item in data:
        reading = item.get("reading", "")
        if reading:
            hiragana = jaconv.kata2hira(reading)
            item["k_reading"] = furitohan_str(hiragana)
        else:
            item["k_reading"] = ""
            
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    # Copy to frontend
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'public', 'data', 'japanese_words_1.json')
    with open(frontend_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    # Copy to dist
    dist_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dist', 'data', 'japanese_words_1.json')
    if os.path.exists(os.path.dirname(dist_path)):
        with open(dist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    print("Successfully updated JSON files with k_reading.")

if __name__ == '__main__':
    update_json()
