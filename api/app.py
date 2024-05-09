"""
A module that implements api routing and core business logic for the IFCViz backend. 
"""

import re
import io
import json
import gzip
from hashlib import sha256
from flask import Flask, request, make_response, send_file, render_template
from flask_cors import CORS
from typing import Optional

from flask import Flask
from .ifcparser import parse
from . import db

import ifcopenshell
import ifcopenshell.file
import ifcopenshell.validate


app = Flask(__name__, template_folder='../webapp')
CORS(app)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = 'uploads/'

rsha256hash = re.compile(r"^[a-fA-F0-9]{64}$")


def secure_filename(filename: str) -> str:
    return "".join(x for x in filename if x.isalnum())



def try_or_default(default):
    ''' Function wrapper, returns `default` if an exception is raised in the function `f`. This is required
        due to Flask raising exceptions even when they are caught in an except block'''
    def wrap(f):
        def inner(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                return default
        return inner
    return wrap


def dump_contents(contents: bytes, filename: str) -> bool:
    '''
    Helper to prevent try/catch inside Flask app 
    '''
    with open(app.config['UPLOAD_FOLDER']+filename, 'wb') as f:
        f.write(contents)

    return True

@app.route("/receive/<string:filehash>")
def send(filehash: str):
    """
    Implements the GET endpoint /receive/<string:filehash>, a route that 
    allows for the download of an IFC file with a given hash.
    """
    ERROR_INVALID = make_response(json.dumps({'error': 'invalid hash provided'}),   400)
    ERROR_NO_FILE = make_response(json.dumps({'error': 'file does not exist'}),     400)

    if not rsha256hash.fullmatch(filehash):
        return ERROR_INVALID

    filename: str = secure_filename(filehash)
    if not db.analysis_exists(filename):
        return ERROR_NO_FILE

    c = db.get_file(filename)
    # print(c)
    contents: io.BytesIO = io.BytesIO(c)
    return send_file(contents, mimetype='application/gzip', as_attachment=False)


@app.route("/upload", methods=['POST'])
def upload():
    """
    Implements the POST endpoint /upload/, which will store and analyze an IFC file and
    return its hash for future reference to the file. 
    """
    ERROR_NO_CONT = make_response(json.dumps({'error': 'no content provided'}),     400)
    ERROR_NO_GZIP = make_response(json.dumps({'error': 'file not gzipped'}),        400)
    ERROR_INVALID = make_response(json.dumps({'error': 'file is not ifc'}),         400)

    # KEEP THE CODE BELLOW IF SWITCHING TO FORM FILE UPLOAD STYLE!!!!!
    # ================================================================
    # if 'file' not in request.files or request.files[0].filename == '':
    #     flash('No file part included')
    #
    #     return ERROR_NO_FILE
    #
    # file = request.files['file']
    # ================================================================

    contents: bytes = request.data
    if not contents:
        return ERROR_NO_CONT

    gzip_file: gzip.GzipFile = gzip.GzipFile(fileobj=io.BytesIO(request.data), mode='rb')
    gzip_contents: Optional[bytes] = try_or_default(None)(gzip_file.read)()
    gzip_file.close()

    if not gzip_contents:
        return ERROR_NO_GZIP
    
    filename: str = sha256(contents).hexdigest()
    if db.analysis_exists(filename):
        return make_response(json.dumps({'fileid': filename}))

    model_reader_safe = try_or_default(None)(ifcopenshell.file().from_string)
    model: Optional[ifcopenshell.file] = model_reader_safe(gzip_contents.decode())
    logger: Optional[ifcopenshell.validate.json_logger] \
        = ifcopenshell.validate.json_logger()
    error: Optional[int] = try_or_default(-1)(ifcopenshell.validate.validate)(
        model, logger)
    if error == -1:
        return ERROR_INVALID

    # Todo: Test single mods
    # analysis = parse(contents, "floors")
    # analysis = parse(contents, "windows")
    # analysis = parse(contents, "walls")
    analysis = parse(contents, "all")
    db.new_analysis(filename, contents, analysis)

    return make_response(json.dumps({'fileid': filename}), 200)


@app.route("/metadata/<string:filehash>")
def metadata(filehash: str):
    ERROR_INVALID = make_response(json.dumps({'error': 'invalid hash provided'}),   400)
    ERROR_NO_FILE = make_response(json.dumps({'error': 'file does not exist'}),     400)

    if not rsha256hash.fullmatch(filehash):
        return ERROR_INVALID

    filename: str = secure_filename(filehash)
    if not db.analysis_exists(filename):
        return ERROR_NO_FILE

    return db.get_metadata(filehash)

@app.route("/", methods=["GET"])
def parsing_result():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
