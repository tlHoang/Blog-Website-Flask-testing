from app import db, app
from os import path

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

def create_user(username, email, password):
    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()
    return user

if __name__ == "__main__":
    with app.app_context():
        if not path.exists('app.db'):
            print("Creating database tables...")
            db.create_all()
            print("Done!")