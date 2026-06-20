from datetime import datetime
from extensions import db

class TrackLyrics(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    artist = db.Column(db.String(255), nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    processed_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    play_count = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    youtube_video_id = db.Column(db.String(100), nullable=True)
    youtube_video_ids = db.Column(db.Text, nullable=True)
    translated_title_info = db.Column(db.Text, nullable=True)
    translated_album_info = db.Column(db.Text, nullable=True)
    theme_colors = db.Column(db.Text, nullable=True)

class DailyVisitor(db.Model):
    date = db.Column(db.Date, primary_key=True)
    count = db.Column(db.Integer, default=0)

class ArtistBoard(db.Model):
    id = db.Column(db.String(100), primary_key=True) # Spotify Artist ID
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ArtistComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, nullable=True)
    nickname = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    track_id = db.Column(db.String(100), nullable=False)
    track_name = db.Column(db.String(255), nullable=True)
    track_artist = db.Column(db.String(255), nullable=True)
    track_image = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GuitarPreset(db.Model):
    __bind_key__ = 'guitar_db'
    __tablename__ = 'guitar_presets'

    id = db.Column(db.String(36), primary_key=True) # UUID string
    name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255))
    bpm = db.Column(db.Float, default=90.0)
    row_count = db.Column(db.Integer, default=4)
    data = db.Column(db.JSON, nullable=False) # 전체 JSON 프리셋 데이터

def get_or_create_track(track_id, **kwargs):
    track = TrackLyrics.query.get(track_id)
    if not track:
        track = TrackLyrics(id=track_id, processed_data="[]", **kwargs)
        db.session.add(track)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            track = TrackLyrics.query.get(track_id)
            if not track:
                track = TrackLyrics(id=track_id, processed_data="[]", **kwargs)
                db.session.add(track)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
    return track
