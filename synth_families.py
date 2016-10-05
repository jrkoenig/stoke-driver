
import synth, sys, pickle

NUM_WORKERS = 2
RUNS = 500
TIMEOUT = 10*1000*1000
RESULTS_FILE = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"

def make_target((def_in, live_out, instrs)):
    t = synth.SynthTarget()
    t.def_in = def_in
    t.live_out = live_out
    t.target = ".f:\n" + "\n".join(instrs) +"\nretq\n"
    t.testcases = ""
    return t

families = pickle.load(open("families.pickle", "r"))
for num, progs in families:
    if len(progs[-1][2]) > 20:
        print "---", num, "---"
        print progs[-1]
        jobs = [{'name':str(num)+"-"+str(len(p[2])),'target':make_target(p),'limit': TIMEOUT, 'silent': True, 'args':['--generate_testcases']} for p in progs]

jobs = jobs * RUNS

#print "Running on", NUM_WORKERS, "cores"
#print "Running ", RUNS, "times per program, i.e.", len(jobs), "total"
#print "Writing to", RESULTS_FILE
#synth.run_stoke_jobs(RESULTS_FILE, jobs, NUM_WORKERS)
