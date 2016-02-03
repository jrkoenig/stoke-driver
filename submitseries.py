
import threading, json, os, sys, gzip, random

import pg, pgmq, targetbuilder


RUNS = 500
TIMEOUT = 20*1000*1000
series_name = "strict_nonincrease"
progs = ['p{:02d}'.format(i+1) for i in range(25)]
progs = [p for p in progs if p != 'p19']
#progs = ['p18','p10','p11','p12','p17','p20','p21','p24']
#progs = ['p19']
randomize = False
stoke_hash = 'd2a59111d6d16590d93e7bb39f3bece2de0aabdf'

def main():
    targets = targetbuilder.make_all_from_c("gulwani/gulwani.json")
    conn = pg.connect('jrkoenig')
    c = conn.cursor()
    c.execute("INSERT INTO distr_series (name, stoke_hash) VALUES (%s, %s) RETURNING id;", [series_name, stoke_hash])
    conn.commit()
    (series_id,) = c.fetchone()
    print "Starting series "+series_name+"("+str(series_id)+")"
    
    jobs = [{'series': series_id,
              'name': n, 'stoke_hash': stoke_hash, 'target': targets[n].to_json(),
              'timeout':TIMEOUT} for n in progs]
    l = []
    for j in jobs:
        l.extend([j]*RUNS)
    if randomize:
        l = random.sample(l, len(l))
    jobs = [pg.Binary(json.dumps(j, separators=(',',':'), ensure_ascii=True)) for j in l]
    s = pgmq.Server(conn, "synth_queue")
    s.post_all(jobs)
    conn.close()

if __name__ == "__main__":
    main()
