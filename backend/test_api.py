import requests
import json

data = {
    "lyrics": "hello\nworld",
    "track_id": "manual_test_track_2",
    "title": "Manual Title",
    "artist": "Manual Artist",
    "cover_url": "http://example.com/cover.jpg"
}

res = requests.post("http://127.0.0.1:5001/api/lyrics/process", json=data)
print("POST status:", res.status_code)

res2 = requests.get("http://127.0.0.1:5001/api/lyrics/manual_test_track_2")
print("GET status:", res2.status_code)
print("GET data:", res2.json() if res2.status_code == 200 else res2.text)
