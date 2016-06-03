
import threading, json, os, sys, gzip, random

import pg, pgmq, targetbuilder


RUNS = 250
TIMEOUT = 20*1000*1000
series_name = "double_proposal_1.5_all"
progs = ['p{:02d}'.format(i+1) for i in range(25)]
progs = [p for p in progs if p != 'p19']

args = ['--instruction_mass', str(100),
        "--opcode_mass", str(100),
        "--opcode_width_mass", str(100),
        "--operand_mass", str(100),
        "--local_swap_mass", str(100),
        "--global_swap_mass", str(100),
        "--rotate_mass", str(100),
        "--double_mass", str(15)]

randomize = False
stoke_hash = 'ef7db106c65eabffda674818f9f8f177583d3230'

def main():
    targets = targetbuilder.make_all_from_c("gulwani/gulwani.json")
    conn = pg.connect('jrkoenig')
    c = conn.cursor()
    c.execute("INSERT INTO distr_series (name, stoke_hash) VALUES (%s, %s) RETURNING id;", [series_name, stoke_hash])
    conn.commit()
    (series_id,) = c.fetchone()
    sys.stdout.write("Starting series "+series_name+"("+str(series_id)+") ")
    sys.stdout.flush()
    
    jobs = [{'series': series_id,
              'name': n, 'stoke_hash': stoke_hash, 'target': targets[n].to_json(),
              'timeout':TIMEOUT, 'captures':[], 'args':args} for n in progs]
    
    s = pgmq.Server(conn, "synth_queue")
    for j in jobs:
        l = [j]*RUNS
        j = [pg.Binary(json.dumps(j, separators=(',',':'), ensure_ascii=True)) for j in l]
        s.post_all(j)
        sys.stdout.write(".")
        sys.stdout.flush()
    conn.close()
    sys.stdout.write(" done.\n")

if __name__ == "__main__":
    main()
