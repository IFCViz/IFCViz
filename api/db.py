"""
## db.py
###This module provides primitives for interacting with the IFCViz database.  
  
IFCViz requires a postgresql database to be running at ``port 5432`` with default
credentials on the same host as the server. For more information about configuring
and running postgresql with docker, see (set up postgres)[postgres.html]
"""

import psycopg
from psycopg.rows import TupleRow
from typing import Optional


def get_conn():
    '''
    Receive a connection handle to the postgres instance. This is a prerequisite
    for all interactions with the database.
    ''' 
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")

def query_one_row(query: str, tuple: tuple, result: bool = True) -> Optional[TupleRow]:
    '''
        Run an arbitrary prepared-statement query on the database and return up to one
        row. Queries that do not return rows should have the result parameter set as false. Should the SQL query return more than one row, only one will
        be returned to the caller. 

        query: the prepared-statement query to be run. Variables are marked with 
        %s (or in rare cases %t, %b --- do not use these without consulting the postgres docs) format string specifiers.

        tuple: A tuple containing variables to be bound to the prepared statement.
        eg, if the query contains three instances of the format specifier %s, the tuple must contain three values.

        result: Set to false when no rows are returned

    '''
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
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,), False)


def get_metadata(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,), False)[2]


def get_file(filehash):
    return query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,))[1]

def delete_analysis(filehash: str):
    return query_one_row("DELETE FROM analysis WHERE id=%s", (filehash,), False)

def analysis_exists(filehash: str) -> bool:
    res = query_one_row("SELECT * FROM analysis WHERE id=%s", (filehash,))
    return res != None