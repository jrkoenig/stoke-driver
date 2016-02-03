
import psycopg2
import os

def _load_db_str(f):
    f = f if f.endswith(".db") else f + ".db"
    for prefix in [os.getcwd(), os.path.expanduser("~")]:
        try:
            contents = open(os.path.join(prefix,f),"r").readlines()
            if len(contents) != 1:
                raise RuntimeException("bad db")
            else:
                return contents[0].strip()
        except:
            pass
    raise RuntimeException("Database not found")

def connect(db):
    return psycopg2.connect(_load_db_str(db))

Binary = psycopg2.Binary
