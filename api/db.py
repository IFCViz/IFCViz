import psycopg
from typing import Optional


def get_conn():
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")

def new_analysis(filehash, file_content, parsed) -> bool:
    try:
        conn = get_conn()
        cur = conn.cursor()

        q: str = "INSERT INTO analysis (id, ifc_file, parsed) VALUES (%s, %s, %s)"
        cur.execute(q, (filehash, file_content, parsed))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_analysis(filehash: str) -> Optional[psycopg.rows.TupleRow]:
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM analysis WHERE id=%s", (filehash,))
        res = cur.fetchone()
        conn.close()
        return res
    except:
        return None


def get_metadata(filehash: str) -> Optional[str]:
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM analysis WHERE id=%s", (filehash,))
        res = cur.fetchone()[2]
        conn.close()
        return res
    except:
        return None


def get_file(filehash: str) -> Optional[bytes]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis WHERE id=%s", (filehash,))
    res = cur.fetchone()[1]
    conn.close()
    return res

def delete_analysis(filehash: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM analysis WHERE id=%s", (filehash,))
    conn.close()

def analysis_exists(filehash: str) -> bool:
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM analysis WHERE id=%s", (filehash,))
        res = cur.fetchone()
        conn.close()
        return res != None
    except:
        return False