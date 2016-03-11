
import threading, json, os, sys, gzip, random

import pg, pgmq, targetbuilder


RUNS = 250
TIMEOUT = 20*1000*1000
series_name = "searchexpt_logs"
progs = ['p{:02d}'.format(i+1) for i in range(25)]
progs = [p for p in progs]
randomize = False
stoke_hash = 'b3d92cbb5fa488cbce923a6db583899c0295dedc'

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
              'timeout':TIMEOUT, 'captures':[], 'args':[]} for n in progs]
    
    s = pgmq.Server(conn, "synth_queue")
    for j in jobs:
        l = [j]*RUNS
        j = [pg.Binary(json.dumps(j, separators=(',',':'), ensure_ascii=True)) for j in l]
        s.post_all(j)
    conn.close()

if __name__ == "__main__":
    main()
