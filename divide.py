
import synth, sys, pickle, random
from collections import defaultdict

NUM_WORKERS = 52
RUNS = 100
TIMEOUT = 5*1000*1000
RESULTS_FILE = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"

class Target(object):
    def __init__(self, di, lo, instrs):
        self.def_in = di
        self.live_out = lo
        self.instrs = instrs
    def __str__(self):
        return "(" + ",".join(self.def_in) +")->("+",".join(self.live_out)+") {" + "; ".join(self.instrs) + "}"
    def size(self): return len(instrs)
def interesting_instr(x):
    if x.startswith("movq ") or x.startswith("movl "):
        return False
    if x == "xchgw %ax, %ax":
        return False
    return True

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

def has_xmm_input(target):
    return "%xmm" in " ".join(target.def_in) or "%ymm" in " ".join(target.def_in)
    
def main():
    families = pickle.load(open("libs.families.pickle", "r"))
    lists = defaultdict(list)
    for i, f in enumerate(families):
        size = len(filter(interesting_instr,f.head.instrs))
        if size <= 10 and not has_xmm_input(f.head):
            lists[size].append(i)

    for i,j in lists.items():
        random.shuffle(j)
        print i, len(j)
    
    items = zip(*[[(size,j) for j in l] for size,l in lists.items()])
    items = [item for sublist in items for item in sublist]
    a = open("a.txt", "w")
    b = open("b.txt", "w")
    i = 0
    for i,item in enumerate(items):
        f = [a,b][random.randint(0,1)]
        f.write(str(item[1])+" "+str(item[0])+"\n")
        
main()
