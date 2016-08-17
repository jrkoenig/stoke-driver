
import synth, sys, json

NUM_WORKERS = 52
RUNS = 100
TIMEOUT = 1000000
RESULTS_FILE = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"

p = synth.SynthTarget.from_json(json.load(open("gray32.json")))
codes = open("all_gray8_successes.txt").read().split("===")[1:]
jobs = [{'name':"gray8-"+str(i),'target':p,'limit':TIMEOUT,'args':[], 'init':c} for i,c in enumerate(codes)]
jobs += [{'name':"gray8",'target':p,'limit':TIMEOUT,'args':[]} for i in range(5)]
jobs = jobs * RUNS

print "Running on", NUM_WORKERS, "cores"
print "Running ", RUNS, "times per program, i.e.", len(jobs), "total"
print "Writing to", RESULTS_FILE
synth.run_stoke_jobs(RESULTS_FILE, jobs, NUM_WORKERS)
