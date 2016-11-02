
import synth, sys, cPickle, random, threading, json
from synth import pmap, stokerunner

NUM_WORKERS = 28
RUNS = 1
TIMEOUT = 50*1000*1000
RESULTS_FILE = sys.argv[2] if len(sys.argv) > 2 else "results.jsonl"

class Target(object):
    def __init__(self, di, lo, instrs):
        self.def_in = di
        self.live_out = lo
        self.instrs = instrs
    def __str__(self):
        return "(" + ",".join(self.def_in) +")->("+",".join(self.live_out)+") {" + "; ".join(self.instrs) + "}"
    def size(self): return len(instrs)

class Family(object):
    def __init__(self, target):
        self.head = target
        self.rest = []
    def __str__(self):
        return str(self.head) + " & " + ",".join(map(str,self.rest))
    def merge_if_contained(self, target):
        if self.head.def_in != target.def_in:
            return False
        s = len(self.head.instrs)
        if s == len(target.instrs) and self.head.instrs == target.instrs:
            # target is the same as head. ignore so we don't get duplicates
            return True
        elif s < len(target.instrs) and self.head.instrs == target.instrs[:s]:
            self.rest.append((s,self.head.live_out))
            self.head = target
            return True
        elif s > len(target.instrs) and target.instrs == self.head.instrs[:len(target.instrs)]:
            self.rest.append((len(target.instrs), target.live_out))
            self.rest.sort(key = lambda x: x[0])
            return True
        else:
            return False

families = None

def make_target(target):
    t = synth.SynthTarget()
    t.def_in = target.def_in
    t.live_out = filter(lambda x: x != "%af", target.live_out)
    t.target = ".f:\n" + "\n".join(target.instrs) +"\nretq\n"
    t.testcases = ""
    return t

def run_trial(i):
    job = {'name':str(i),'target':make_target(families[i].head),'limit': TIMEOUT, 'silent': True, 'args':['--generate_testcases']}
    name = job['name']
    verbose = 'silent' not in job or not job['silent']
    runner = stokerunner.StokeRunner()
    runner.setup(job['target'], job['init'] if 'init' in job else None)
    limit = job['limit']
    runner.add_args(["--timeout_iterations", str(limit)])
    runner.add_args(["--timeout_seconds", str(900)])
    runner.add_args(["--validator_must_support"])
    #runner.add_args(["--cycle_timeout", str(limit)])
    #runner.add_args(["--double_mass", "0"])
    runner.add_args(job['args'])
    runner.launch()
    runner.wait()
    
    open("logs/"+str(i)+".stdout", "w").write(runner.get_file("stdout.out"))
    open("logs/"+str(i)+".stderr", "w").write(runner.get_file("stderr.out"))
    j = runner.get_file("search.json")
    open("logs/"+str(i)+".json", "w").write(j if j is not None else "")
    
    if runner.successful():
        print "STOKE finished on " + name
        r = analyze_result(job, runner)
    else:
        print "STOKE Failed on "+name+"!!!"
        r = {"name":name,"error":True}
    runner.cleanup()
    return r

def analyze_result(job, runner):
    r = json.loads(runner.get_file("search.json"))
    output = {'iters': r["statistics"]["total_iterations"],
              'examples': r["statistics"]["total_counterexamples"],
              'name': job['name'],
              'verified': r['verified']}
    return output

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

def main():
    global families
    print "Loading families..."
    families = cPickle.load(open("libs.families.pickle", "r"))
    print "Picking assigned jobs..."
    jobs = [i for i,f in enumerate(families)]
    random.shuffle(jobs)
    print "Running on", NUM_WORKERS, "cores"
    print "Running ", RUNS, "times per program, i.e.", len(jobs), "total"
    print "Writing to", RESULTS_FILE
    run_stoke_jobs(RESULTS_FILE, jobs, NUM_WORKERS)

main()
