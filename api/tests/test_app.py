import json
from api.app import app, secure_filename


def test_secure_filename():
    assert secure_filename('') == ''
    assert secure_filename('\x00\x01\x02\x03\x04\x05') == ''
    assert secure_filename('!@#$%^&*()_+-=\\<>|/{}') == ''
    assert secure_filename('\x010Dla1#1!23##@\x00\x05@24F') == '0Dla112324F'

def test_upload():
    res_empty = app.test_client().post('/upload')
    assert res_empty.data == json.dumps({'error': 'file not gzipped'}).encode('ASCII')
    assert res_empty.status_code == 400

    # ================================================================================

def test_send():
    pass