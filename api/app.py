import os
import io
import json
import gzip
from hashlib import sha256
from flask import Flask, request, make_response


app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = 'uploads/'


def secure_filename(filename: str) -> str:
    return "".join(x for x in filename if x.isalpha())

def try_or_default(default):
    def wrap(f):
        def inner(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print(e)
                return default
        return inner
    return wrap


@app.route("/upload/", methods=['POST'])
def upload():
    ERROR_NO_FILE = make_response(json.dumps({'error': 'no uploaded file'}), 400)
    ERROR_NO_GZIP = make_response(json.dumps({'error': 'file not gzipped'}), 400)

    # KEEP THE CODE BELLOW IF SWITCHING TO FORM FILE UPLOAD STYLE!!!!!
    # ================================================================
    # if 'file' not in request.files or request.files[0].filename == '':
    #     flash('No file part included')
    #
    #     return ERROR_NO_FILE
    #
    # file = request.files['file']
    # ================================================================

    GzipFileSafe = try_or_default(None)(gzip.GzipFile)
    gzip_file = GzipFileSafe(fileobj=io.BytesIO(request.data), mode='rb')
    
    if not gzip_file:
        return ERROR_NO_GZIP

    if not gzip_file.read():
        return ERROR_NO_FILE
    
    filename = sha256(gzip_file.read()).hexdigest()
    return make_response(json.dumps({'fileid': filename}), 200)

if __name__ == '__main__':
    app.run(use_reloader = False)