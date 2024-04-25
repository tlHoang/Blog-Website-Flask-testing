from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from os import path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tanphat'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(255))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_name = request.form['name']
        session.permanent = True
        if user_name:
            session['user'] = user_name
            found_user = User.query.filter_by(username = user_name).first()
            if found_user:
                session['id'] = found_user.id
                session['username'] = found_user.username
                session['email'] = found_user.email
                session['password'] = found_user.password
                return redirect(url_for('user'))
            else:
                session['id'] = 'found_user.id'
                session['username'] = 'found_user.username'
                session['email'] = 'found_user.email'
                session['password'] = 'found_user.password'
                return redirect(url_for('user'))
    return render_template('test.html')

@app.route('/user', methods=['POST', 'GET'])
def user():
    if 'user' in session:
        return render_template('print.html', id=session['id'], username=session['username'], email=session['email'], password=session['password'])
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        if not path.exists('user.db'):
            db.create_all()
            print("Created database!")
    app.run(debug=True)