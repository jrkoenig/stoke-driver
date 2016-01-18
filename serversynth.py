#!/usr/bin/python
import json, os, sys, gzip, random, shutil, time

import stokerunner, synthtarget, stokeversion
import pg, pgmq

parallelism = 4

class WorkTask(object):
    def __init__(self, job, msg, build_cache):
        self.timeout = job['timeout']
        self.name = job['name']
        self.series = job['series']
        self.message = msg
        self.runner = None
        self.stokev = None
        try:
            self.stokev = build_cache.get_by_hash(job['stoke_hash'])
            path = self.stokev.acquire()
            if path is None:
                raise RuntimeError("No stoke could be found")
            self.runner = stokerunner.StokeRunner(path)
            self.runner.setup(job['target'])
            self.runner.add_args(["--cycle_timeout", str(self.timeout),
                                  "--timeout_iterations", str(self.timeout)])
            self.runner.launch()
            print "Started run of stoke"
        except:
            if self.runner is not None: self.runner.cleanup()
            raise
    def work(self, conn):
        if not self.runner.finished():
            return False
        if self.runner.successful():
            r = json.loads(self.runner.get_file("search.json"))
            final = r["best_correct"] if r['success'] else r["best_yet"]
            output = {'iters': r["statistics"]["total_iterations"],
                      'limit': self.timeout,
                      'name': self.name,
                      'correct': r['success'], 'cost': final['cost'],
                      'asm': final['code'],
                      'elapsed': r["statistics"]["total_search_time"]}
            print "Finished", self.name, "in", output['iters'], "iterations"
            c = conn.cursor()
            c.execute("INSERT INTO distr_output(series, result_json) VALUES (%s,%s) RETURNING id",
               [self.series, json.dumps(output, separators=(',',':'), ensure_ascii=True)])
            (output_id,) = c.fetchone()
            #if 'captures' in r:
            #    for f, d in r['captures'].items():
            #        c.execute("INSERT INTO distr_gz_captures(output, file, data) VALUES (%s,%s,%s)",
            #                   [output_id, f, pg.Binary(d)])
            conn.commit()
        else:
            print 'Stoke failed on '+self.name+'!!'
        self.stokev.release()
        self.message.finish()
        self.runner.cleanup()
        return True

accepting_jobs = True

def main():
    global accepting_jobs
    inprogress = []
    print "Connecting to server..."
    conn = pg.connect('jrkoenig')
    s = pgmq.Server(conn, "synth_queue")
    build_cache = stokeversion.BuildCache()
    print "Scanning build cache..."
    build_cache.scan()
    print "Building targets"
    targets = synthtarget.make_all_from_c("gulwani/gulwani.json")

    print "Ready for jobs..."
    while True:

        msg = None
        if accepting_jobs and len(inprogress) == 0:
            msg = s.get_sync()
        elif accepting_jobs and len(inprogress) < parallelism:
            msg = s.get_async()
        else:
            time.sleep(0.005)

        if msg is not None:
            job = json.loads(str(msg.data()), 'utf-8')
            job['target'] = targets[job['target']]
            try:
                inprogress.append(WorkTask(job, msg, build_cache))
            except Exception as e:
                print "Failed to launch stoke"
                print e
                msg.abort()
                accepting_jobs = False
        next_inprogress = []
        for task in inprogress:
            if not task.work(conn):
                next_inprogress.append(task)
        inprogress = next_inprogress

        if not accepting_jobs and len(inprogress) == 0:
            print "Exiting..."
            break
    print "Exited main loop"
if __name__ == "__main__":
    main()
