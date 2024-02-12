from flask import Flask
from parser import parse

app = Flask(__name__)

@app.route("/")
def hello_world():
    return f"<p>{parse('../test_files/simple_house.ifc')}</p>"