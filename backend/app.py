from flask import Flask, jsonify, request, send_from_directory
import json
from flask_cors import CORS
import os
import requests
import base64
import urllib.parse
from lyrics_processor import process_lyrics_text
from colorthief import ColorThief
import io
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')

from datetime import datetime

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

# DB Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'lyrics.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TrackLyrics(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    artist = db.Column(db.String(255), nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    processed_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    play_count = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN likes INTEGER DEFAULT 0"))
        db.session.commit()
    except Exception:
        db.session.rollback()

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    # 기존 레거시 앱 정적 파일 지원 (예: /파일명)
    legacy_dir = '/home/conansjh20/static'
    req_path = request.path.lstrip('/')
    legacy_file = os.path.join(legacy_dir, req_path)
    
    # 보안: 파일 경로가 legacy_dir 내부에 있는지 확인 (경로 조작 방지)
    if os.path.exists(legacy_file) and os.path.isfile(legacy_file):
        # 상위 폴더 접근(..) 차단
        if os.path.abspath(legacy_file).startswith(os.path.abspath(legacy_dir)):
            return send_from_directory(legacy_dir, req_path)
            
    return send_from_directory(app.static_folder, 'index.html')
CORS(app)  # 개발 환경에서 프론트엔드와 백엔드 포트가 다를 때 CORS 문제 방지

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Flask Backend!"})


SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

def get_spotify_token():
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

@app.route('/api/spotify/search', methods=['GET'])
def spotify_search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
        
    token = get_spotify_token()
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=10"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    result = requests.get(url, headers=headers)
    return jsonify(json.loads(result.content))

@app.route('/api/spotify/artist/<artist_id>/top-tracks', methods=['GET'])
def spotify_artist_top_tracks(artist_id):
    token = get_spotify_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=KR"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    result = requests.get(url, headers=headers)
    return jsonify(json.loads(result.content))

@app.route('/api/spotify/playlist/<playlist_id>/latest', methods=['GET'])
def get_playlist_latest(playlist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    res = requests.get(playlist_url, headers=headers)
    data = res.json()
    total = data.get('tracks', {}).get('total', 0)
    
    if total > 0:
        offset = max(0, total - 100)
        tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100&offset={offset}"
        res2 = requests.get(tracks_url, headers=headers)
        data2 = res2.json()
        
        items = data2.get('items', [])
        items.reverse()
        result_tracks = [item['track'] for item in items if item.get('track')]
        return jsonify({"tracks": result_tracks})
    
    return jsonify({"tracks": []})


YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

@app.route('/api/youtube/search', methods=['GET'])
def youtube_search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
        
    url1 = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&videoEmbeddable=true&key={YOUTUBE_API_KEY}&maxResults=5"
    url2 = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query} live&type=video&videoEmbeddable=true&key={YOUTUBE_API_KEY}&maxResults=5"
    url3 = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query} cover&type=video&videoEmbeddable=true&key={YOUTUBE_API_KEY}&maxResults=5"
    
    video_ids = []
    seen = set()
    
    for url in [url1, url2, url3]:
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
        return jsonify({"videoIds": video_ids, "videoId": video_ids[0]})
    else:
        return jsonify({"error": "No video found"}), 404

@app.route('/api/songlist', methods=['GET'])
def get_songlist():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = TrackLyrics.query.order_by(TrackLyrics.likes.desc(), TrackLyrics.title.asc()).paginate(page=page, per_page=per_page, error_out=False)
    
    songs = []
    for track in pagination.items:
        songs.append({
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "cover_url": track.cover_url,
            "created_at": track.created_at.isoformat() if track.created_at else None,
            "play_count": track.play_count,
            "likes": track.likes or 0,
            "lyrics": json.loads(track.processed_data)
        })
        
    return jsonify({
        "songs": songs,
        "total_pages": pagination.pages,
        "current_page": page,
        "total_items": pagination.total
    })

@app.route('/api/lyrics/<track_id>', methods=['GET'])
def get_lyrics(track_id):
    track = TrackLyrics.query.get(track_id)
    if track:
        if track.play_count is None:
            track.play_count = 0
        track.play_count += 1
        db.session.commit()
        return jsonify(json.loads(track.processed_data))
    return jsonify({"error": "Not found"}), 404

@app.route('/api/songlist/<track_id>', methods=['PUT'])
def update_song(track_id):
    track = TrackLyrics.query.get(track_id)
    if not track:
        return jsonify({"error": "Not found"}), 404
        
    data = request.json
    if 'title' in data:
        track.title = data['title']
    if 'artist' in data:
        track.artist = data['artist']
    if 'lyrics' in data:
        track.processed_data = json.dumps(data['lyrics'])
        
    db.session.commit()
    return jsonify({"message": "Updated successfully"})

@app.route('/api/songlist/<track_id>', methods=['DELETE'])
def delete_song(track_id):
    track = TrackLyrics.query.get(track_id)
    if not track:
        return jsonify({"error": "Not found"}), 404
        
    db.session.delete(track)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})

@app.route('/api/translate/info', methods=['POST'])
def translate_info():
    data = request.json
    title = data.get('title', '')
    album = data.get('album', '')
    
    title_proc = process_lyrics_text(title)
    album_proc = process_lyrics_text(album)
    
    return jsonify({
        "title": title_proc[0] if title_proc else None,
        "album": album_proc[0] if album_proc else None
    })

@app.route('/api/lyrics/process', methods=['POST'])
def process_lyrics():
    data = request.json
    if not data or 'lyrics' not in data:
        return jsonify({"error": "No lyrics provided"}), 400
        
    raw_lyrics = data['lyrics']
    track_id = data.get('track_id')
    title = data.get('title')
    artist = data.get('artist')
    cover_url = data.get('cover_url')
    
    processed = process_lyrics_text(raw_lyrics)
    
    # DB 저장 로직
    if track_id:
        existing_track = TrackLyrics.query.get(track_id)
        if existing_track:
            existing_track.processed_data = json.dumps(processed)
            if title: existing_track.title = title
            if artist: existing_track.artist = artist
            if cover_url: existing_track.cover_url = cover_url
        else:
            new_track = TrackLyrics(
                id=track_id, 
                processed_data=json.dumps(processed),
                title=title,
                artist=artist,
                cover_url=cover_url
            )
            db.session.add(new_track)
        db.session.commit()
        
    return jsonify(processed)

@app.route('/api/song/<track_id>/likes', methods=['GET'])
def get_likes(track_id):
    track = TrackLyrics.query.get(track_id)
    if track:
        return jsonify({"likes": track.likes or 0})
    return jsonify({"likes": 0})

@app.route('/api/song/<track_id>/like', methods=['POST'])
def add_like(track_id):
    data = request.json or {}
    track = TrackLyrics.query.get(track_id)
    if not track:
        track = TrackLyrics(
            id=track_id,
            title=data.get('title'),
            artist=data.get('artist'),
            cover_url=data.get('cover_url'),
            processed_data='[]',
            likes=1
        )
        db.session.add(track)
    else:
        if track.likes is None:
            track.likes = 0
        track.likes += 1
    db.session.commit()
    return jsonify({"likes": track.likes})

@app.route('/api/color', methods=['GET'])
def get_color():
    img_url = request.args.get('url')
    if not img_url:
        return jsonify({"error": "No url provided"}), 400
        
    try:
        r = requests.get(img_url, timeout=5)
        f = io.BytesIO(r.content)
        color_thief = ColorThief(f)
        dominant_color = color_thief.get_color(quality=1)
        palette = color_thief.get_palette(color_count=4, quality=1)
        return jsonify({
            "dominant": dominant_color,
            "palette": palette
        })
    except Exception as e:
        print("Color extraction failed:", e)
        return jsonify({"error": str(e)}), 500


##########################################################
# 라디오 라우트
@app.route('/radio/mon', methods=['GET'])
def get_channel1():
    with open("data/radio/mon.json", "r", encoding="utf-8") as mon:
        data = json.load(mon)
        return jsonify(data)

@app.route('/radio/tue', methods=['GET'])
def get_channel2():
    with open("data/radio/tue.json", "r", encoding="utf-8") as tue:
        data = json.load(tue)
        return jsonify(data)

@app.route('/radio/wed', methods=['GET'])
def get_channel3():
    with open("data/radio/wed.json", "r", encoding="utf-8") as wed:
        data = json.load(wed)
        return jsonify(data)

@app.route('/radio/thu', methods=['GET'])
def get_channel4():
    with open("data/radio/thu.json", "r", encoding="utf-8") as thu:
        data = json.load(thu)
        return jsonify(data)

@app.route('/radio/fri', methods=['GET'])
def get_channel5():
    with open("data/radio/fri.json", "r", encoding="utf-8") as fri:
        data = json.load(fri)
        return jsonify(data)

@app.route('/radio/sat', methods=['GET'])
def get_channel6():
    with open("data/radio/sat.json", "r", encoding="utf-8") as sat:
        data = json.load(sat)
        return jsonify(data)

@app.route('/radio/sun', methods=['GET'])
def get_channel7():
    with open("data/radio/sun.json", "r", encoding="utf-8") as sun:
        data = json.load(sun)
        return jsonify(data)

#############################################################
# Engcross 신버전 Helper Functions

def read_json(filepath):
    """지정된 경로의 JSON 파일을 읽어서 파이썬 딕셔너리로 반환합니다."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(filepath, data):
    """파이썬 딕셔너리 데이터를 지정된 경로의 JSON 파일로 저장합니다."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)

def check_new_rank(filepath):
    """랭킹 조회 공통 로직: JSON을 읽어 {이름: 점수} 형태로 반환"""
    result = read_json(filepath)
    # result = {"홍길동": [1, "1234"], ...} 
    # new_result = {"홍길동": 1, ...} 로 변환
    new_result = {key: value[0] for key, value in result.items()}
    return jsonify(new_result)

def update_new_rank(filepath):
    """랭킹 업데이트 공통 로직: name, password를 확인하고 점수를 올리거나 새로 추가"""
    name = request.args.get("name")
    password = request.args.get("password")
    
    # 인자 누락 에러 방지 처리 (KeyError 방지)
    if not name or not password:
        return "Missing name or password", 400

    rank = read_json(filepath)
    
    if name in rank:
        # 기존 유저일 경우 비밀번호 확인
        if password == rank[name][1]:
            rank[name][0] += 1
            write_json(filepath, rank)
            return "updated"
        else:
            return "wrongPass"
    else:
        # 신규 유저일 경우 추가
        rank[name] = [1, password]
        write_json(filepath, rank)
        return "new"

#########################################################################
# Engcross 신버전 API (랭킹 조회)

@app.route('/engcross/newrankelementary', methods=['GET'])
def check_new_rank_elementary():
    return check_new_rank("data/engcross/newElementaryRank.json")

@app.route('/engcross/newrankmiddlehigh', methods=['GET'])
def check_new_rank_middlehigh():
    return check_new_rank("data/engcross/newMiddlehighRank.json")

@app.route('/engcross/newranktoeic', methods=['GET'])
def check_new_rank_toeic():
    return check_new_rank("data/engcross/newToeicRank.json")

@app.route('/engcross/newrankofficer', methods=['GET'])
def check_new_rank_officer():
    return check_new_rank("data/engcross/newOfficerRank.json")

#########################################################################
# Engcross 신버전 API (랭킹 업데이트)

@app.route('/engcross/newone', methods=['GET'])
def new_update_rankE():
    return update_new_rank("data/engcross/newElementaryRank.json")

@app.route('/engcross/newtwo', methods=['GET'])
def new_update_rankM():
    return update_new_rank("data/engcross/newMiddlehighRank.json")

@app.route('/engcross/newthree', methods=['GET'])
def new_update_rankT():
    return update_new_rank("data/engcross/newToeicRank.json")

@app.route('/engcross/newfour', methods=['GET'])
def new_update_rankO():
    return update_new_rank("data/engcross/newOfficerRank.json")

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
