
import stokerunner, stokeversion, targetbuilder
import threading, json, os, sys, gzip, random, time, pmap
from synthtarget import SynthTarget

NUM_WORKERS = 52

RUNS = 250
TIMEOUT = 10000000
filename = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"
log_prefix = filename if not filename.endswith(".jsonl") else filename[:-6]
TARGET_DIR = os.path.abspath("./")
RESULTS_FILE = os.path.join(TARGET_DIR, filename)
LOG_DIR = os.path.join(TARGET_DIR, "logs")

next = 0
def save_result(f, l, runner, name, target):

    r = json.loads(runner.get_file("search.json"))
    #print r
    s = r["best_correct"]
    output = {'iters': r["statistics"]["total_iterations"],
              'limit': TIMEOUT,
              'name': name,
              'verified': r['verified'], 'success': r['success'],
              'starting_cost': r['starting_cost'],
              'cost': s['cost'],
              'asm': s['code'],
              'elapsed': r["statistics"]["total_time"]}
    global next
    log_filename = ''
    lognum = 0
    with l:
        lognum = next
        next += 1
        output ['log'] = lognum
        f.write(json.dumps(output,  separators=(',',':'), ensure_ascii=True)+"\n")
        f.flush()
    for capture in []:
        gz_data = runner.get_gz_file(capture)
        if gz_data is not None:
            with open(os.path.join(LOG_DIR, name+"-"+str(lognum)+"-"+capture+".gz"), 'wb') as logout:
                logout.write(gz_data)
        else:
            print "Could not save " + capture

def load_targets(folder):
    targets = []
    for a in os.listdir(folder):
        j = json.load(open(os.path.join(folder, a)))
        target = SynthTarget.from_json(j)
        targets.append((a, target))
    return targets
def main():
    filelock = threading.Lock()

    if not os.path.isdir(LOG_DIR):
       os.makedirs(LOG_DIR)
    with open(RESULTS_FILE,"w") as f:
        def run_trial((name, target)):
            runner = stokerunner.StokeRunner()
            runner.setup(target)
            runner.add_args(["--timeout_iterations", str(TIMEOUT)])
            runner.add_args(["--cycle_timeout", str(TIMEOUT)])
            runner.add_args(["--double_mass", "0"])

            runner.launch()
            runner.wait()
            if runner.successful():
                print "STOKE finished on " + name
                for line in runner.get_file("stdout.out").split("\n"):
                    if line.endswith("is unsupported."):
                        print line
                save_result(f, filelock, runner, name, target)
            else:
                print "STOKE Failed on "+name+"!!!"
                #print runner.get_file("stdout.out")
                print runner.get_file("stderr.out")
            runner.cleanup()

        progs = load_targets("targets/gulwani")
        l = list(progs * RUNS)

        print "Running on", NUM_WORKERS, "cores"
        print "Running ", RUNS, "times per program, i.e.", len(l), "total"
        print "Writing to", RESULTS_FILE
        results = pmap.pmap(run_trial, l, NUM_WORKERS)

if __name__ == "__main__":
    main()
