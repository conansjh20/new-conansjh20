from app import app, db, ArtistBoard, ArtistComment
from sqlalchemy import text

with app.app_context():
    print("Dropping ArtistBoard and ArtistComment...")
    db.session.execute(text("DROP TABLE IF EXISTS artist_board"))
    db.session.execute(text("DROP TABLE IF EXISTS artist_comment"))
    db.session.commit()
    print("Recreating all tables...")
    db.create_all()
    print("Done.")
