
import synth, sys, pickle, random

NUM_WORKERS = 2
RUNS = 5
TIMEOUT = 50*1000
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


def make_target(target):
    t = synth.SynthTarget()
    t.def_in = target.def_in
    t.live_out = target.live_out
    t.target = ".f:\n" + "\n".join(target.instrs) +"\nretq\n"
    t.testcases = ""
    return t

def main():
    print "Loading families..."
    families = pickle.load(open("libs.families.pickle", "r"))
    print "Picking assigned jobs..."
    initial_jobs = []
    assert len(sys.argv) > 1
    for l in open(sys.argv[1]):
        if l.strip() != "":
            i = int(l.strip())
            f = families[i]
            initial_jobs.append({'name':str(i)+"-"+str(len(f.head.instrs)),'target':make_target(f.head),'limit': TIMEOUT, 'silent': False, 'args':['--generate_testcases']})
            
    random.shuffle(initial_jobs)
    jobs = []
    print "Building jobs..."
    for job in initial_jobs:
        jobs.extend([job]*RUNS)

    print "Running on", NUM_WORKERS, "cores"
    print "Running ", RUNS, "times per program, i.e.", len(jobs), "total"
    print "Writing to", RESULTS_FILE
    synth.run_stoke_jobs(RESULTS_FILE, jobs, NUM_WORKERS)

main()
