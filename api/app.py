from flask import Flask
from parser import parse

app = Flask(__name__)

@app.route("/")
def hello_world():
    jsn = parse('../test_files/simple_house.ifc')
    return f"<p>{jsn}</p>"