
import stokerunner, targetbuilder, pmap
import json, sys, os, threading
from synthtarget import SynthTarget

def run_trial(job):
    name = job['name']
    verbose = 'silent' not in job or not job['silent']
    runner = stokerunner.StokeRunner()
    runner.setup(job['target'], job['init'] if 'init' in job else None)
    limit = job['limit']
    runner.add_args(["--timeout_iterations", str(limit)])
    runner.add_args(["--cycle_timeout", str(limit)])
    #runner.add_args(["--double_mass", "0"])
    runner.add_args(job['args'])
    runner.launch()
    runner.wait()
    if runner.successful():
        if verbose:
            print "STOKE finished on " + name
        r = analyze_result(job, runner)
    else:
        if verbose:
            print "STOKE Failed on "+name+"!!!"
            print runner.get_file("stdout.out")
            print runner.get_file("stderr.out")
        r = None
    runner.cleanup()
    return r

def analyze_result(job, runner):
    r = json.loads(runner.get_file("search.json"))
    s = r["best_correct"] if r['success'] else r["best_yet"]
    output = {'iters': r["statistics"]["total_iterations"],
              'limit': job['limit'],
              'name': job['name'],
              'verified': r['verified'],
              'success': r['success'],
              #'starting_cost': r['starting_cost'],
              'cost': s['cost'],
              'code': s['code'],
              'elapsed': r["statistics"]["total_time"],
              'extra_args': job['args'],
              'log': runner.get_file("search.log")}
    return output

def load_targets(directory):
    targets = []
    for a in os.listdir(directory):
        if not a.endswith(".json"): continue
        j = json.load(open(os.path.join(directory, a)))
        target = SynthTarget.from_json(j)
        targets.append((a[:-5], target))
    return targets

def run_stoke_jobs(jsonl_file, jobs, NUM_WORKERS=2):
    f = open(jsonl_file, "w")
    lock = threading.Lock()
    def run_and_save(job):
        r = run_trial(job)
        if r is not None:
            with lock:
                f.write(json.dumps(r,  separators=(',',':'), ensure_ascii=True)+"\n")
                f.flush()
    r = pmap.pmap(run_and_save, jobs, NUM_WORKERS)
    f.close()
