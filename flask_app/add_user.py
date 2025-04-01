import sys
from app import app
from models import db, User

def add_user(username):
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists.")
            return
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' added successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_user.py <username>")
    else:
        add_user(sys.argv[1])
