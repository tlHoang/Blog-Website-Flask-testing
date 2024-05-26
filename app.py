from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

if __name__ == "__main__":

    from routes import *
    app.logger.info("Starting app")
    app.run(debug=True)