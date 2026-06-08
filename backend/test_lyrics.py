import sys
import os

sys.path.append(os.path.abspath('backend'))

from lyrics_processor import process_lyrics_text

results = process_lyrics_text("こういう先生")
with open("backend/test_lyrics_output.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(str(r) + "\n")
