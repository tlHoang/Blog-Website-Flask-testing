from flask import Flask

app = Flask(__name__) # create an app instance

@app.route("/") # at the end point /
def hello_world():
    return "<p>Hello, World!</p>"

# if name = app.py or wsgi.py no need --app 