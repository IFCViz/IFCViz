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
def dump_gzip(contents: bytes, filename: str) -> bool:
    with open(app.config['UPLOAD_FOLDER']+filename, 'wb') as f:
        f.write(contents)

    return True



@app.route("/upload/", methods=['POST'])
def upload():
    ERROR_NO_FILE = make_response(json.dumps({'error': 'no uploaded file'}),        400)
    ERROR_NO_GZIP = make_response(json.dumps({'error': 'file not gzipped'}),        400)
    ERROR_NO_SAVE = make_response(json.dumps({'error': 'file cannot be saved'}),    500)
    ERROR_F_EXIST = make_response(json.dumps({'error': 'file already exists'}),     500)

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

    # Flushes the read buffer automatically that's why we save the contents
    contents = gzip_file.read()
    if not contents:
        gzip_file.close()
        return ERROR_NO_FILE
    
    gzip_file.close()

    filename = sha256(contents).hexdigest()
    # If implementing hash storage in DB use query instead of `os.path.isfile``
    if os.path.isfile(app.config['UPLOAD_FOLDER']+filename):
        return ERROR_F_EXIST

    if not try_or_default(False)(dump_gzip)(contents, filename):
        return ERROR_NO_SAVE
    
    return make_response(json.dumps({'fileid': filename}), 200)

if __name__ == '__main__':
    app.run(use_reloader = False)