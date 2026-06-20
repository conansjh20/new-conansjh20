import os
import json
import base64
import requests
from flask import Blueprint, jsonify, request
from models import TrackLyrics
from extensions import db

spotify_bp = Blueprint('spotify_bp', __name__)

def get_spotify_token():
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

@spotify_bp.route('/api/spotify/search', methods=['GET'])
def spotify_search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    items = []
    seen_ids = set()

    # 1. Search in local database first
    try:
        db_tracks = TrackLyrics.query.filter(
            db.or_(
                TrackLyrics.title.ilike(f'%{query}%'),
                TrackLyrics.artist.ilike(f'%{query}%')
            )
        ).limit(10).all()

        for t in db_tracks:
            items.append({
                "id": t.id,
                "name": t.title,
                "artists": [{"name": t.artist, "id": ""}],
                "album": {
                    "name": "Local DB",
                    "images": [{"url": t.cover_url}] if t.cover_url else []
                },
                "duration_ms": 0,
                "is_local_db": True
            })
            seen_ids.add(t.id)
    except Exception as e:
        print("DB search error:", e)

    # 2. Fetch from Spotify API if we need more results
    if len(items) < 15:
        try:
            token = get_spotify_token()
            url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=15"
            headers = {
                "Authorization": f"Bearer {token}"
            }

            result = requests.get(url, headers=headers)
            spotify_data = result.json()

            if "tracks" in spotify_data and "items" in spotify_data["tracks"]:
                for st in spotify_data["tracks"]["items"]:
                    if st["id"] not in seen_ids:
                        items.append(st)
                        seen_ids.add(st["id"])
                        if len(items) >= 15:
                             break
        except Exception as e:
            print("Spotify search error:", e)

    return jsonify({"tracks": {"items": items}})

@spotify_bp.route('/api/spotify/artist/<artist_id>/top-tracks', methods=['GET'])
def spotify_artist_top_tracks(artist_id):
    token = get_spotify_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=KR"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    result = requests.get(url, headers=headers)
    return jsonify(json.loads(result.content))

@spotify_bp.route('/api/spotify/playlist/<playlist_id>/latest', methods=['GET'])
def get_playlist_latest(playlist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}

    playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    res = requests.get(playlist_url, headers=headers)
    data = res.json()
    total = data.get('tracks', {}).get('total', 0)

    if total > 0:
        offset = max(0, total - 50)
        tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset={offset}&market=KR"
        res2 = requests.get(tracks_url, headers=headers)
        data2 = res2.json()

        items = data2.get('items', [])
        items.reverse()
        result_tracks = [item['track'] for item in items if item.get('track')][:50]
        return jsonify({"tracks": result_tracks})

    return jsonify({"tracks": []})

@spotify_bp.route('/api/spotify/track/<track_id>', methods=['GET'])
def spotify_get_track(track_id):
    try:
        token = get_spotify_token()
        url = f"https://api.spotify.com/v1/tracks/{track_id}?market=KR"
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return jsonify(res.json())
        else:
            return jsonify({"error": "Failed to fetch track"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
