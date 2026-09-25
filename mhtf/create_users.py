from app import app, db, User
from werkzeug.security import generate_password_hash

USERS = [
    ("admin", "Admin123!", "admin", "de"),
    ("test", "Test123!", "user", "de"),
]

with app.app_context():
    for username, password, role, language in USERS:
        user = User.query.filter_by(username=username).first()
        if not user:
            db.session.add(User(
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                language=language,
                active=True,
            ))
            print(f"Angelegt: {username}")
        else:
            print(f"Bereits vorhanden: {username}")
    db.session.commit()
