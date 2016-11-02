
import synth, sys

NUM_WORKERS = 52
RUNS = 5
TIMEOUT = 10000000
RESULTS_FILE = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"

progs = synth.load_targets("targets/gulwani")
jobs = [{'name':n,'target':p,'limit':TIMEOUT,'args':[]} for (n,p) in progs if n != 'p19']
jobs = jobs * RUNS

print "Running on", NUM_WORKERS, "cores"
print "Running ", RUNS, "times per program, i.e.", len(jobs), "total"
print "Writing to", RESULTS_FILE
synth.run_stoke_jobs(RESULTS_FILE, jobs, NUM_WORKERS)
