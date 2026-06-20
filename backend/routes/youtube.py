import os
import json
import requests
from flask import Blueprint, jsonify, request
from models import TrackLyrics, get_or_create_track
from extensions import db

youtube_bp = Blueprint('youtube_bp', __name__)

@youtube_bp.route('/api/youtube/search', methods=['GET'])
def youtube_search():
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
    query = request.args.get('q')
    track_id = request.args.get('track_id')

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    if track_id:
        track = TrackLyrics.query.get(track_id)
        if track and track.youtube_video_ids:
            try:
                cached_ids = json.loads(track.youtube_video_ids)
                if cached_ids:
                    return jsonify({"videoIds": cached_ids, "videoId": cached_ids[0]})
            except Exception:
                pass
        elif track and track.youtube_video_id:
            return jsonify({"videoIds": [track.youtube_video_id], "videoId": track.youtube_video_id})

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&videoEmbeddable=true&key={YOUTUBE_API_KEY}&maxResults=15"

    video_ids = []
    seen = set()

    try:
        res = requests.get(url).json()
        if "items" in res:
            for item in res["items"]:
                vid = item["id"]["videoId"]
                if vid not in seen:
                    video_ids.append(vid)
                    seen.add(vid)
    except Exception as e:
        print("Youtube search error:", e)

    if len(video_ids) > 0:
        first_video_id = video_ids[0]

        if track_id:
            track = get_or_create_track(track_id)
            track.youtube_video_id = first_video_id
            track.youtube_video_ids = json.dumps(video_ids)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return jsonify({"videoIds": video_ids, "videoId": first_video_id})
    else:
        return jsonify({"error": "No video found"}), 404
