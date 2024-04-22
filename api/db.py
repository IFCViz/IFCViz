import psycopg
from typing import Optional


def get_conn():
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")

def query_one_row(query_str, tuple):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))
    res = cur.fetchone()
    conn.commit()
    conn.close()
    return res


def new_analysis(filehash, file_content, parsed):
    query_one_row.execute("INSERT INTO analysis (id, ifc_file, parsed) VALUES (%s, %s, %s)", (format_hash(filehash), file_content, parsed))


def get_analysis(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))


def get_metadata(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))[2]


def get_file(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))[1]

def delete_analysis(filehash: str):
    return query_one_row("DELETE FROM analysis WHERE id=%s", (format_hash(filehash),))

def analysis_exists(filehash: str) -> bool:
    res = query_one_row("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))
    return res != None