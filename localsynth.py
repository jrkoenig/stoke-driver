
import stokerunner, synthtarget, stokeversion, targetbuilder
import threading, json, os, sys, gzip, random, time, pmap

NUM_WORKERS = 1

RUNS = 1
TIMEOUT = 1*1000*1000
filename = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"
log_prefix = filename if not filename.endswith(".jsonl") else filename[:-6]
TARGET_DIR = os.path.abspath("./")
RESULTS_FILE = os.path.join(TARGET_DIR, filename)
LOG_DIR = os.path.join(TARGET_DIR, "logs")

next = 0
def save_result(f, l, runner, name, target):

    r = json.loads(runner.get_file("search.json"))
    s = r["current"]
    output = {'iters': r["statistics"]["total_iterations"],
              'limit': TIMEOUT,
              'name': name,
              'correct': r['success'], 'cost': s['cost'], 'asm': s['code'],
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
    for log, data in [("search", runner.get_gz_file("search.binlog"))]:
        with open(os.path.join(LOG_DIR, name+"-"+str(lognum)+"-"+log+".gz"), 'wb') as logout:
            if data is not None:
                logout.write(data)
def main():
    targets = targetbuilder.make_all_from_c("gulwani/gulwani.json")
    filelock = threading.Lock()

    if not os.path.isdir(LOG_DIR):
       os.makedirs(LOG_DIR)
    with open(RESULTS_FILE,"w") as f:
        def run_trial((name, target)):

            runner = stokerunner.StokeRunner()
            runner.setup(target)
            runner.add_args(["--timeout_iterations", str(TIMEOUT)])
            runner.launch()
            runner.wait()
            if runner.successful():
                save_result(f, filelock, runner, name, target)
            else:
                print "STOKE Failed on "+name+"!!!"
                print runner.get_file("stderr.out")
                print runner.get_file("stdout.out")
            runner.cleanup()

        progs = ['p{:02d}'.format(i+1) for i in range(25)]
        progs = [(p,targets[p]) for p in progs if p != 'p19']

        print "Running on", NUM_WORKERS, "cores"
        print "Running ", RUNS, "times per program"
        print "Writing to", RESULTS_FILE
        l = list(progs * RUNS)
        results = pmap.pmap(run_trial, l, NUM_WORKERS)

if __name__ == "__main__":
    main()
