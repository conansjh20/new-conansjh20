import json
from lyrics_processor import process_lyrics_text
with open('test.json', 'w', encoding='utf8') as f:
    f.write(json.dumps(process_lyrics_text('コーヒー'), ensure_ascii=False))
