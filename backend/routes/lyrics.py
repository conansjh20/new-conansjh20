import json
import requests
import io
from flask import Blueprint, jsonify, request
from colorthief import ColorThief
from lyrics_processor import process_lyrics_text
from models import TrackLyrics, get_or_create_track
from extensions import db

lyrics_bp = Blueprint('lyrics_bp', __name__)

@lyrics_bp.route('/api/songlist', methods=['GET'])
def get_songlist():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = TrackLyrics.query.order_by(TrackLyrics.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

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
            "youtube_video_id": track.youtube_video_id,
            "translated_title_info": json.loads(track.translated_title_info) if getattr(track, 'translated_title_info', None) else None,
            "translated_album_info": json.loads(track.translated_album_info) if getattr(track, 'translated_album_info', None) else None,
            "theme_colors": json.loads(track.theme_colors) if getattr(track, 'theme_colors', None) else None,
            "lyrics": json.loads(track.processed_data) if track.processed_data else []
        })

    return jsonify({
        "songs": songs,
        "total_pages": pagination.pages,
        "current_page": page,
        "total_items": pagination.total
    })

@lyrics_bp.route('/api/lyrics/<track_id>', methods=['GET'])
def get_lyrics(track_id):
    track = TrackLyrics.query.get(track_id)
    if track:
        if track.play_count is None:
            track.play_count = 0
        track.play_count += 1
        db.session.commit()
        return jsonify(json.loads(track.processed_data))
    return jsonify({"error": "Not found"}), 404

@lyrics_bp.route('/api/songlist/<track_id>', methods=['PUT'])
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

@lyrics_bp.route('/api/songlist/<track_id>', methods=['DELETE'])
def delete_song(track_id):
    track = TrackLyrics.query.get(track_id)
    if not track:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(track)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})

@lyrics_bp.route('/api/translate/info', methods=['POST'])
def translate_info():
    data = request.json
    track_id = data.get('track_id')
    artist = data.get('artist')
    cover_url = data.get('cover_url')
    title_raw = data.get('title', '')
    album_raw = data.get('album', '')

    if track_id:
        track = get_or_create_track(track_id)
        updated = False
        if title_raw and not track.title:
            track.title = title_raw
            updated = True
        if artist and not track.artist:
            track.artist = artist
            updated = True
        if cover_url and not track.cover_url:
            track.cover_url = cover_url
            updated = True
        if updated:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        if track and track.translated_title_info:
            return jsonify({
                "title": json.loads(track.translated_title_info),
                "album": json.loads(track.translated_album_info) if track.translated_album_info else None
            })

    title = data.get('title', '')
    album = data.get('album', '')

    title_proc = process_lyrics_text(title)
    title_info = title_proc[0] if title_proc else None

    album_proc = process_lyrics_text(album)
    album_info = album_proc[0] if album_proc else None

    if track_id:
        track = get_or_create_track(track_id)
        if title_info:
            track.translated_title_info = json.dumps(title_info)
        if album_info:
            track.translated_album_info = json.dumps(album_info)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    return jsonify({
        "title": title_info,
        "album": album_info
    })

@lyrics_bp.route('/api/lyrics/process', methods=['POST'])
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

    if track_id:
        existing_track = get_or_create_track(track_id, title=title, artist=artist, cover_url=cover_url)
        existing_track.processed_data = json.dumps(processed)
        if title: existing_track.title = title
        if artist: existing_track.artist = artist
        if cover_url: existing_track.cover_url = cover_url
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    return jsonify(processed)

@lyrics_bp.route('/api/song/<track_id>/likes', methods=['GET'])
def get_likes(track_id):
    track = TrackLyrics.query.get(track_id)
    if track:
        return jsonify({"likes": track.likes or 0})
    return jsonify({"likes": 0})

@lyrics_bp.route('/api/song/<track_id>/like', methods=['POST'])
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

@lyrics_bp.route('/api/color', methods=['GET'])
def get_color():
    img_url = request.args.get('url')
    track_id = request.args.get('track_id')
    if not img_url:
        return jsonify({"error": "No url provided"}), 400

    if track_id:
        track = TrackLyrics.query.get(track_id)
        if track and track.theme_colors:
            return jsonify(json.loads(track.theme_colors))

    try:
        r = requests.get(img_url, timeout=5)
        f = io.BytesIO(r.content)
        color_thief = ColorThief(f)
        dominant_color = color_thief.get_color(quality=10)
        palette = color_thief.get_palette(color_count=4, quality=10)

        result = {
            "dominant": dominant_color,
            "palette": palette
        }

        if track_id:
            track = get_or_create_track(track_id)
            track.theme_colors = json.dumps(result)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return jsonify(result)
    except Exception as e:
        print("Color extraction failed:", e)
        return jsonify({"error": str(e)}), 500

@lyrics_bp.route('/api/lyrics/auto-fetch', methods=['GET'])
def auto_fetch_lyrics():
    """
    LRCLIB 무료 API를 통해 가사 원문을 자동으로 가져오고, 
    기존 로직(MeCab 독음 + DeepL 번역)을 거쳐 최종 결과를 반환합니다.
    """
    title = request.args.get('title')
    artist = request.args.get('artist')
    
    if not title or not artist:
        return jsonify({"error": "title and artist parameters are required"}), 400
        
    try:
        # 1. LRCLIB API를 통해 가사 검색
        # 'get' 엔드포인트 시도 (정확한 매칭)
        url = "https://lrclib.net/api/get"
        params = {
            "track_name": title,
            "artist_name": artist
        }
        res = requests.get(url, params=params, timeout=10)
        
        lrclib_data = None
        if res.status_code == 200:
            lrclib_data = res.json()
        else:
            # 'get'이 실패하면 'search' 엔드포인트로 첫 번째 결과 시도
            search_url = "https://lrclib.net/api/search"
            # q 파라미터로 제목+가수 검색
            search_res = requests.get(search_url, params={"q": f"{title} {artist}"}, timeout=10)
            if search_res.status_code == 200:
                data = search_res.json()
                if isinstance(data, list) and len(data) > 0:
                    lrclib_data = data[0]
                    
        if not lrclib_data:
            return jsonify({"error": "Lyrics not found on LRCLIB"}), 404
            
        # syncedLyrics가 있으면 우선 사용, 없으면 plainLyrics 사용
        raw_lyrics = lrclib_data.get('syncedLyrics') or lrclib_data.get('plainLyrics')
        
        if not raw_lyrics:
            return jsonify({"error": "Lyrics content is empty"}), 404
            
        # 2. 기존 process_lyrics_text 함수로 독음 및 번역 처리
        processed = process_lyrics_text(raw_lyrics)
        
        return jsonify({
            "title": title,
            "artist": artist,
            "source": "lrclib",
            "lyrics": processed
        })
        
    except Exception as e:
        print("Auto fetch lyrics error:", e)
        return jsonify({"error": str(e)}), 500
