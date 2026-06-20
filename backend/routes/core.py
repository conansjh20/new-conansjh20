import os
from flask import Blueprint, jsonify, request, send_from_directory, make_response
from models import DailyVisitor, TrackLyrics
from extensions import db
from datetime import date
from sqlalchemy import func

core_bp = Blueprint('core_bp', __name__)

@core_bp.route('/')
def serve():
    from flask import current_app
    response = make_response(send_from_directory(current_app.static_folder, 'index.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@core_bp.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Flask Backend!"})

@core_bp.route('/api/visit', methods=['POST'])
def record_visit():
    try:
        today = date.today()
        visitor = DailyVisitor.query.get(today)
        if not visitor:
            visitor = DailyVisitor(date=today, count=1)
            db.session.add(visitor)
        else:
            visitor.count += 1
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Visit record error:", e)
        return jsonify({"error": str(e)}), 500

@core_bp.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        # 1. Total visitors
        total_visitors = db.session.query(func.sum(DailyVisitor.count)).scalar() or 0

        # 2. Daily visitors (today)
        today = date.today()
        today_visitor = DailyVisitor.query.get(today)
        daily_visitors = today_visitor.count if today_visitor else 0

        # 3. Top clicked songs (ordered by play_count)
        top_tracks = TrackLyrics.query.filter(TrackLyrics.play_count != None).order_by(TrackLyrics.play_count.desc()).limit(20).all()

        songs = []
        for track in top_tracks:
            songs.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "cover_url": track.cover_url,
                "play_count": track.play_count or 0
            })

        return jsonify({
            "total_visitors": total_visitors,
            "daily_visitors": daily_visitors,
            "top_songs": songs
        })
    except Exception as e:
        print("Stats error:", e)
        return jsonify({"error": str(e)}), 500
