import pg
import json, os, sys, gzip, shutil, io

def main():
    itercounts = {}

    #os.mkdir("logs/")
    fname = 'search.binlog'
    series = 8
    conn = pg.connect('jrkoenig')
    c = conn.cursor(name="results_cursor")
    c.itersize = 4
    c.execute("SELECT data,distr_output.result_json FROM distr_gz_captures INNER JOIN distr_output ON output = distr_output.id WHERE series = %s AND file=%s;",     [series, fname]);
    i = 0
    for (data,json) in c:
        
        sys.stdout.write(".")
        sys.stdout.flush()
        with open("logs/{:04}-{}.gz".format(i, fname), "wb") as f:
            #bstream = io.BytesIO(data)
            #g = gzip.GzipFile(fname, "rb", 9, bstream)
            #shutil.copyfileobj(g, f)
            f.write(data)
        with open("logs/{:04}-search.json".format(i), "w") as f:
            f.write(json)
        i += 1
    conn.commit()
    conn.close()
if __name__ == "__main__":
    main()
