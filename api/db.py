import psycopg

def get_conn():
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")

def new_analysis(filehash, file, parsed):
    conn = get_conn()
    conn.execute("INSERT INTO analysis (%s, %s, %s)", (filehash, file, parsed))
    conn.commit()
    conn.close()

def get_analysis(filehash):
    conn = get_conn()
    conn.execute("SELECT * FROM analysis WHERE id=%s", (filehash))
    res = conn.fetchone()
    conn.close()
    return conn
