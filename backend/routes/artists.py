from flask import Blueprint, jsonify, request
from models import ArtistBoard, ArtistComment
from extensions import db
from datetime import datetime

artists_bp = Blueprint('artists_bp', __name__)

@artists_bp.route('/api/artists', methods=['GET'])
def get_artists():
    artists = ArtistBoard.query.order_by(ArtistBoard.created_at.desc()).all()
    return jsonify({
        "artists": [
            {
                "id": a.id,
                "name": a.name,
                "image_url": a.image_url,
                "created_at": a.created_at.isoformat()
            } for a in artists
        ]
    })

@artists_bp.route('/api/artists', methods=['POST'])
def create_artist():
    data = request.json
    artist_id = data.get('id')
    name = data.get('name')
    image_url = data.get('image_url')

    if not artist_id or not name:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    artist = ArtistBoard.query.get(artist_id)
    if not artist:
        artist = ArtistBoard(id=artist_id, name=name, image_url=image_url)
        db.session.add(artist)
        db.session.commit()

    return jsonify({"success": True, "artist_id": artist.id})

@artists_bp.route('/api/artists/<artist_id>', methods=['GET'])
def get_artist(artist_id):
    artist = ArtistBoard.query.get(artist_id)
    if not artist:
        return jsonify({"error": "Artist not found"}), 404
    return jsonify({
        "id": artist.id,
        "name": artist.name,
        "image_url": artist.image_url,
        "created_at": artist.created_at.isoformat()
    })

@artists_bp.route('/api/artists/<artist_id>/comments', methods=['GET'])
def get_comments(artist_id):
    comments = ArtistComment.query.filter_by(artist_id=artist_id).order_by(ArtistComment.created_at.asc()).all()
    return jsonify({
        "comments": [
            {
                "id": c.id,
                "artist_id": c.artist_id,
                "parent_id": c.parent_id,
                "nickname": c.nickname,
                "content": c.content,
                "track_id": c.track_id,
                "track_name": c.track_name,
                "track_artist": c.track_artist,
                "track_image": c.track_image,
                "created_at": c.created_at.isoformat()
            } for c in comments
        ]
    })

@artists_bp.route('/api/artists/<artist_id>/comments', methods=['POST'])
def create_comment(artist_id):
    data = request.json
    nickname = data.get('nickname')
    password = data.get('password')
    content = data.get('content')
    track_id = data.get('track_id')
    parent_id = data.get('parent_id')
    
    if not all([nickname, password, content, track_id]):
        return jsonify({"success": False, "error": "Missing fields"}), 400

    comment = ArtistComment(
        artist_id=artist_id,
        parent_id=parent_id,
        nickname=nickname,
        password_hash=password, # Note: using raw password for simplicity matching frontend
        content=content,
        track_id=track_id,
        track_name=data.get('track_name'),
        track_artist=data.get('track_artist'),
        track_image=data.get('track_image')
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({"success": True, "comment_id": comment.id})

@artists_bp.route('/api/artists/comments/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    data = request.json
    password = data.get('password')
    content = data.get('content')

    comment = ArtistComment.query.get(comment_id)
    if not comment:
        return jsonify({"success": False, "error": "Comment not found"}), 404

    if comment.password_hash != password:
        return jsonify({"success": False, "error": "Incorrect password"}), 403

    comment.content = content
    db.session.commit()
    return jsonify({"success": True})

@artists_bp.route('/api/artists/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    data = request.json
    password = data.get('password')

    comment = ArtistComment.query.get(comment_id)
    if not comment:
        return jsonify({"success": False, "error": "Comment not found"}), 404

    if comment.password_hash != password:
        return jsonify({"success": False, "error": "Incorrect password"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"success": True})
