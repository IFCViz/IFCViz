import psycopg

def format_hash(hash):
    return "0x" + str(hash)[10]
def get_conn():
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")

def new_analysis(filehash, file_content, parsed):
    conn = get_conn()
    conn.cursor().execute("INSERT INTO analysis (id, ifc_file, parsed) VALUES (%s, %s, %s)", (format_hash(filehash), file_content, parsed))
    conn.commit()
    conn.close()

def get_analysis(filehash):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))
    res = cur.fetchone()
    conn.close()
    return res


def get_metadata(filehash):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))
    res = cur.fetchone()[2]
    conn.close()
    return res


def get_file(filehash):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))
    res = cur.fetchone()[1]
    conn.close()
    return res

def delete_analysis(filehash: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM analysis WHERE id=%s", (format_hash(filehash),))
    conn.close()

def analysis_exists(filehash: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM analysis WHERE id=%s", (format_hash(filehash),))
    res = cur.fetchone()
    conn.close()
    return res != None