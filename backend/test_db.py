from app import db, TrackLyrics, app

with app.app_context():
    track_id = "test_track_123"
    track = TrackLyrics.query.get(track_id)
    if not track:
        track = TrackLyrics(id=track_id, title="Test", artist="Test", processed_data="[]")
        db.session.add(track)
        db.session.commit()
        print("Created test track")
    
    track = TrackLyrics.query.get(track_id)
    track.processed_data = "[\"test\"]"
    try:
        db.session.commit()
        print("Updated test track successfully")
        t2 = TrackLyrics.query.get(track_id)
        print("Fetched:", t2.processed_data)
    except Exception as e:
        print("Error updating test track:", e)
        db.session.rollback()
