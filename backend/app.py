from flask import Flask, request, send_from_directory, make_response
from flask_cors import CORS
import os
from extensions import db
# 임포트 모델: 테이블 생성을 위해 모델이 인식되어야 함
import models

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

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
app.config['SQLALCHEMY_BINDS'] = {
    'guitar_db': 'mysql+pymysql://conansjh20:P020673#1@conansjh20.mysql.pythonanywhere-services.com/conansjh20$guitar'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN likes INTEGER DEFAULT 0"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN youtube_video_id VARCHAR(100)"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN youtube_video_ids TEXT"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN translated_title_info TEXT"))
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN translated_album_info TEXT"))
        db.session.execute(text("ALTER TABLE track_lyrics ADD COLUMN theme_colors TEXT"))
        db.session.commit()
    except Exception:
        db.session.rollback()

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

    response = make_response(send_from_directory(app.static_folder, 'index.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Blueprint 등록
from routes.core import core_bp
from routes.spotify import spotify_bp
from routes.youtube import youtube_bp
from routes.lyrics import lyrics_bp
from routes.radio import radio_bp
from routes.engcross import engcross_bp
from routes.guitar import guitar_bp

app.register_blueprint(core_bp)
app.register_blueprint(spotify_bp)
app.register_blueprint(youtube_bp)
app.register_blueprint(lyrics_bp)
app.register_blueprint(radio_bp)
app.register_blueprint(engcross_bp)
app.register_blueprint(guitar_bp)

if __name__ == '__main__':
    app.run(debug=True)
