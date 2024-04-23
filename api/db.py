import psycopg
from psycopg.rows import TupleRow
from typing import Optional


def get_conn():
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")

def query_one_row(query: str, tuple: tuple, result: bool = True) -> Optional[TupleRow]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, tuple)
    res: Optional[TupleRow] = None
    if result:
        res = cur.fetchone()
    conn.commit()
    conn.close()
    return res


def new_analysis(filehash: str, file_content: bytes, parsed: str):
    q: str = "INSERT INTO analysis (id, ifc_file, parsed) VALUES (%s, %s, %s)"
    query_one_row(q, (filehash, file_content, parsed), False)


def get_analysis(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,))


def get_metadata(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,))[2]


def get_file(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,))[1]

def delete_analysis(filehash: str):
    return query_one_row("DELETE FROM analysis WHERE id=%s", (filehash,), False)

def analysis_exists(filehash: str) -> bool:
    res = query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,))
    return res != None