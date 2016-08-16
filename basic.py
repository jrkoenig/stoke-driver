
import synth, sys

NUM_WORKERS = 2
RUNS = 20
TIMEOUT = 1000000
RESULTS_FILE = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"

progs = synth.load_targets("targets/bit")
jobs = [{'name':n,'target':p,'limit':TIMEOUT,'args':[]} for (n,p) in progs]
l = jobs * RUNS

print "Running on", NUM_WORKERS, "cores"
print "Running ", RUNS, "times per program, i.e.", len(l), "total"
print "Writing to", RESULTS_FILE
synth.run_stoke_jobs(RESULTS_FILE, jobs, NUM_WORKERS)
