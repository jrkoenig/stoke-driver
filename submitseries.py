
import pg, pgmq
import threading, json, os, sys, gzip, random

RUNS = 1
TIMEOUT = 10*1000*1000
series_name = "baseline_for_strict"
progs = ['p{:02d}'.format(i+1) for i in range(25)]
progs = [p for p in progs if p != 'p19']
#progs = ['p18','p10','p11','p12','p17','p20','p21','p24']
randomize = False
stoke_hash = '97ebf1c788345d57ec5d22fc041dfa7c56226063'

def setup():
    conn = pg.connect('jrkoenig')
    s = pgmq.Server(conn, "synth_queue")
    s.recreate()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS distr_output CASCADE;")
    c.execute("DROP TABLE IF EXISTS distr_series CASCADE;")
    c.execute("DROP TABLE IF EXISTS distr_gz_captures CASCADE;")
    c.execute("CREATE TABLE distr_series (id bigserial PRIMARY KEY,\
                                          name varchar(1000),\
                                          stoke_hash varchar(100));")
    c.execute("CREATE TABLE distr_output (id bigserial PRIMARY KEY,\
                                          series bigint REFERENCES distr_series(id),\
                                          result_json text);")
    c.execute("CREATE TABLE distr_gz_captures (id bigserial PRIMARY KEY,\
                                               output bigint REFERENCES distr_output(id),\
                                               file varchar(1000),\
                                               data bytea);")
    s.conn.commit()

def main():
    conn = pg.connect('jrkoenig')
    c = conn.cursor()
    c.execute("INSERT INTO distr_series (name, stoke_hash) VALUES (%s, %s) RETURNING id;", [series_name, stoke_hash])
    conn.commit()
    (series_id,) = c.fetchone()
    print "Starting series "+series_name+"("+str(series_id)+")"

    jobs = [{'series': series_id,
              'name': n, 'stoke_hash': stoke_hash, 'target': n,
              'timeout':TIMEOUT} for n in progs]
    l = list(jobs * RUNS)
    if randomize:
        l = random.sample(l, len(l))
    jobs = [pg.Binary(json.dumps(j, separators=(',',':'), ensure_ascii=True)) for j in l]
    s = pgmq.Server(conn, "synth_queue")
    s.post_all(jobs)
    conn.close()

if __name__ == "__main__":
    main()
