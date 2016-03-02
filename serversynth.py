#!/usr/bin/python
import json, os, sys, gzip, random, shutil, time

import stokerunner, synthtarget, stokeversion
import pg, pgmq

parallelism = 52

class WorkTask(object):
    def __init__(self, job, msg, build_cache):
        self.job = job
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
            self.runner.add_args(["--timeout_iterations", str(self.timeout)])
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
            output = {'iters': r["statistics"]["total_iterations"],
                      'limit': self.timeout,
                      'name': self.name,
                      'correct': r['success'], 'cost': r["current"]['cost'], 'asm': r["current"]['code'],
                      'elapsed': r["statistics"]["total_time"]}
            print "Finished", self.name, "in", output['iters'], "iterations"
            c = conn.cursor()
            c.execute("INSERT INTO distr_output(series, result_json) VALUES (%s,%s) RETURNING id",
               [self.series, json.dumps(output, separators=(',',':'), ensure_ascii=True)])
            (output_id,) = c.fetchone()
            
            for capture in self.job["captures"]:
                gz_data = runner.get_gz_file(capture)
                if gz_data is not None:
                    c.execute("INSERT INTO distr_gz_captures(output, file, data) VALUES (%s,%s,%s)",
                                [output_id, capture, pg.Binary(gz_data)])
                else:
                    print "Could not save " + capture + " for " + self.name
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
    print "Ready for jobs..."
    sys.stdout.flush()
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
            job['target'] = synthtarget.SynthTarget.from_json(job['target'])
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
