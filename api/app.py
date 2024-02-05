import os
from flask import Flask, flash, request, file


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

ERROR_HTML: str = '<h1>ERROR MESSAGE WAS RETURNED</h1>'

def secure_filename(filename: str) -> str:
    return "".join(x for x in filename if x.isalpha())

@app.route("/upload", methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part included')
        return ERROR_HTML

    if file.filename == '':
        flash('No IFC file selected')
        return ERROR_HTML

    filename = secure_filename(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    