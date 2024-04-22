import gzip
import json
import re
from api.app import app, secure_filename

from typing import Optional


def test_secure_filename():
    assert secure_filename('') == ''
    assert secure_filename('\x00\x01\x02\x03\x04\x05') == ''
    assert secure_filename('!@#$%^&*()_+-=\\<>|/{}') == ''
    assert secure_filename('\x010Dla1#1!23##@\x00\x05@24F') == '0Dla112324F'

def test_upload():
    res_empty = app.test_client().post('/upload')
    assert res_empty.data == json.dumps(
        {'error': 'no content provided'}
    ).encode('ASCII')
    assert res_empty.status_code == 400

    res_not_gzip = app.test_client().post('/upload', data=b'not in gzip format')
    assert res_not_gzip.data == json.dumps(
        {'error': 'file not gzipped'}
    ).encode("ASCII")
    assert res_not_gzip.status_code == 400

    res_is_gzip_not_ifc = app.test_client().post(
        '/upload',
        data=gzip.compress(b'not ifc')
    )
    assert res_is_gzip_not_ifc.data == json.dumps(
        {'error': 'file is not ifc'}
    ).encode('ASCII')
    assert res_is_gzip_not_ifc.status_code == 400

    # ================================================================================
    ifc_sample: Optional[bytes] = None
    with open('../ifc_test_files/simple_house.ifc', 'rb') as f:
        ifc_sample = f.read()

    res_is_gzip_is_ifc = app.test_client().post(
        '/upload',
        data=gzip.compress(ifc_sample)
    )
    resha256hash = re.compile(r"^[a-fA-F0-9]{64}$")
    assert res_is_gzip_is_ifc.status == 200

    res_is_gzip_is_ifc_res_json = json.loads(res_is_gzip_is_ifc.data.decode('ASCII'))
    assert resha256hash.fullmatch(res_is_gzip_is_ifc_res_json.get('fileid', '')) != None


def test_send():
    pass