import gzip
import json
import re
from hashlib import sha256

from api.app import app, secure_filename
from api.db import delete_analysis, new_analysis
from api.ifcparser import parse

from typing import Optional


def test_secure_filename():
    assert secure_filename('') == ''
    assert secure_filename('\x00\x01\x02\x03\x04\x05') == ''
    assert secure_filename('!@#$%^&*()_+-=\\<>|/{}') == ''
    assert secure_filename('\x010Dla1#1!23##@\x00\x05@24F') == '0Dla112324F'

def test_upload():
    res_empty = app.test_client().post('/upload')
    assert res_empty.status_code == 400
    assert res_empty.data == json.dumps(
        {'error': 'no content provided'}
    ).encode('ASCII')

    res_not_gzip = app.test_client().post('/upload', data=b'not in gzip format')
    assert res_not_gzip.status_code == 400
    assert res_not_gzip.data == json.dumps(
        {'error': 'file not gzipped'}
    ).encode("ASCII")

    res_is_gzip_not_ifc = app.test_client().post(
        '/upload',
        data=gzip.compress(b'not ifc')
    )
    assert res_is_gzip_not_ifc.status_code == 400
    assert res_is_gzip_not_ifc.data == json.dumps(
        {'error': 'file is not ifc'}
    ).encode('ASCII')

    # ================================================================================
    rsha256hash = re.compile(r"^[a-fA-F0-9]{64}$")

    ifc_sample: Optional[bytes] = None
    with open('../ifc_test_files/simple_house.ifc', 'rb') as f:
        ifc_sample = gzip.compress(f.read())

    # Upload two times the same file
    res_is_gzip_is_ifc_1 = app.test_client().post(
        '/upload',
        data=ifc_sample
    )
    assert res_is_gzip_is_ifc_1.status_code == 200

    res_is_gzip_is_ifc_1_res_json = json.loads(res_is_gzip_is_ifc_1.data.decode('ASCII'))
    assert rsha256hash.fullmatch(res_is_gzip_is_ifc_1_res_json.get('fileid', '')) != None

    res_is_gzip_is_ifc_2 = app.test_client().post(
        '/upload',
        data=ifc_sample
    )
    assert res_is_gzip_is_ifc_2.status_code == 200

    res_is_gzip_is_ifc_2_res_json = json.loads(res_is_gzip_is_ifc_2.data.decode('ASCII'))
    assert rsha256hash.fullmatch(res_is_gzip_is_ifc_2_res_json.get('fileid', '')) != None

    hash1: str = res_is_gzip_is_ifc_1_res_json['fileid']
    hash2: str = res_is_gzip_is_ifc_2_res_json['fileid'] 
    assert hash1 == hash2

    print(hash1)
    # delete_analysis(hash1)

def test_send():
    res_empty = app.test_client().get('/receive/')
    assert res_empty.status_code == 404

    res_invalid_hash_1 = app.test_client().get('/receive/this-is-not-a-valid-hash')
    assert res_invalid_hash_1.status_code == 400
    assert res_invalid_hash_1.data == json.dumps(
        {'error': 'invalid hash provided'}
    ).encode('ASCII')

    res_invalid_hash_2 = app.test_client().get(
        '/receive/dca0031132879efd3c3441c4e25a3e5ae45cec424c79249d2d91273b50eec30c'
    )
    assert res_invalid_hash_2.status_code == 400
    assert res_invalid_hash_2.data == json.dumps(
        {'error': 'file does not exist'}
    ).encode('ASCII')

    # ================================================================================

    ifc_sample: Optional[bytes] = None
    with open('../ifc_test_files/simple_house.ifc', 'rb') as f:
        ifc_sample = gzip.compress(f.read())

    ifc_hash: str = sha256(ifc_sample).hexdigest()
    new_analysis(ifc_hash, ifc_sample, 'this is some analysis data')

    res_ifc_file = app.test_client().get('/receive/'+ifc_hash)
    assert res_ifc_file.status_code == 200
    assert ifc_sample == res_ifc_file.data

    delete_analysis(ifc_hash)

def test_metadata():
    res_empty = app.test_client().get('/metadata/')
    assert res_empty.status_code == 404

    res_invalid_hash_1 = app.test_client().get('/metadata/this-is-not-a-valid-hash')
    assert res_invalid_hash_1.status_code == 400
    assert res_invalid_hash_1.data == json.dumps(
        {'error': 'invalid hash provided'}
    ).encode('ASCII')

    res_invalid_hash_2 = app.test_client().get(
        '/metadata/dca0031132879efd3c3441c4e25a3e5ae45cec424c79249d2d91273b50eec30c'
    )
    assert res_invalid_hash_2.status_code == 400
    assert res_invalid_hash_2.data == json.dumps(
        {'error': 'file does not exist'}
    ).encode('ASCII')

    # ================================================================================
    
    ifc_sample: Optional[bytes] = None
    with open('../ifc_test_files/simple_house.ifc', 'rb') as f:
        ifc_sample = gzip.compress(f.read())

    ifc_parsed: str = parse(ifc_sample)

    ifc_hash: str = sha256(ifc_sample).hexdigest()
    new_analysis(ifc_hash, ifc_sample, ifc_parsed)

    res_manual_add = app.test_client().get('/metadata/'+ifc_hash)
    assert res_manual_add.status_code == 200
    assert res_manual_add.data == ifc_parsed.encode('ASCII')

    delete_analysis(ifc_hash)

    # Integration test with upload/
    res_automatic_add = app.test_client().post('/upload', data=ifc_sample)
    assert res_automatic_add.status_code == 200
    assert json.loads(res_automatic_add.data.decode('ASCII'))['fileid'] == ifc_hash

    res_automatic_add_metadata = app.test_client().get('/metadata/'+ifc_hash)
    assert res_automatic_add_metadata.status_code == 200
    assert res_automatic_add_metadata.data == ifc_parsed.encode('ASCII')