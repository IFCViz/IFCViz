import psycopg

def get_conn():
    return psycopg.connect("dbname=postgres user=postgres host=localhost port=5432")


