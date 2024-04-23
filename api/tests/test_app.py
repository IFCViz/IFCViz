import gzip
import json
import re
from api.app import app, secure_filename
from api.db import delete_analysis

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
    rsha256hash = re.compile(r"^[a-fA-F0-9]{64}$")

    ifc_sample: Optional[bytes] = None
    with open('../ifc_test_files/simple_house.ifc', 'rb') as f:
        ifc_sample = f.read()

    # Upload two times the same file
    res_is_gzip_is_ifc_1 = app.test_client().post(
        '/upload',
        data=gzip.compress(ifc_sample)
    )
    assert res_is_gzip_is_ifc_1.status_code == 200

    res_is_gzip_is_ifc_1_res_json = json.loads(res_is_gzip_is_ifc_1.data.decode('ASCII'))
    assert rsha256hash.fullmatch(res_is_gzip_is_ifc_1_res_json.get('fileid', '')) != None

    res_is_gzip_is_ifc_2 = app.test_client().post(
        '/upload',
        data=gzip.compress(ifc_sample)
    )
    assert res_is_gzip_is_ifc_2.status_code == 200

    res_is_gzip_is_ifc_2_res_json = json.loads(res_is_gzip_is_ifc_2.data.decode('ASCII'))
    assert rsha256hash.fullmatch(res_is_gzip_is_ifc_2_res_json.get('fileid', '')) != None

    delete_analysis(res_is_gzip_is_ifc_2_res_json['fileid'])

def test_send():
    pass