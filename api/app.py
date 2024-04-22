import os
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


def secure_filename(filename: str) -> str:
    return "".join(x for x in filename if x.isalnum())


# Function wrapper, returns `default` if exception rises in `f`. Must have
# ..since Flask ignores try/except and raises the catched error
def try_or_default(default):
    def wrap(f):
        def inner(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                return default
        return inner
    return wrap


# Helper to prevent try/catch inside Flask app
def dump_contents(contents: bytes, filename: str) -> bool:
    with open(app.config['UPLOAD_FOLDER']+filename, 'wb') as f:
        f.write(contents)

    return True

@app.route("/receive/<string:filehash>")
def send(filehash: str):
    ERROR_NO_FILE = make_response(json.dumps({'error': 'file does not exist'}),     400)

    filename: str = secure_filename(filehash)
    if not db.analysis_exists(filename):
        return ERROR_NO_FILE

    contents: bytes = db.get_file(filename)
    return send_file(contents, mimetype='application/gzip', as_attachment=False)


@app.route("/upload", methods=['POST'])
def upload():
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
        model,logger)
    if error == -1:
        return ERROR_INVALID


    analysis = parse(contents)
    db.new_analysis(filename, contents, analysis)

    return make_response(json.dumps({'fileid': filename}), 200)


@app.route("/metadata/<string:filehash>")
def metadata(filehash: str):
    ERROR_INVALID = make_response(json.dumps({'error': 'invalid hash provided'}),     400)

    filename: str = secure_filename(filehash)
    if not db.analysis_exists(filename):
        return ERROR_INVALID

    return db.get_metadata(filehash)

@app.route("/", methods=["GET"])
def parsing_result():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
