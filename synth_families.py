
import time, random, cPickle, json, synth, sys
from synth import stokerunner
from synth.families import FamilyLoader

def run_tasks(task_producer, max_tasks = 2):
    outstanding = []
    try:
        have_more = True
        while have_more or len(outstanding) > 0:
            while have_more and len(outstanding) < max_tasks:
                try:
                    t = next(task_producer)
                    t.start()
                    outstanding.append(t)
                except StopIteration:
                    have_more = False
            time.sleep(0.1)
            outstanding = filter(lambda t: not t.finished(), outstanding)
    except KeyboardInterrupt:
        for o in outstanding:
            o.kill()
            

class StokeTask(object):
    def __init__(self, i, target, out, args = []):
        self.i = i
        self.target = target
        self.output_file = out
        self.extra_args = args
    def start(self):
        self.runner = stokerunner.StokeRunner()
        runner = self.runner
        runner.setup(self.target, None)
        runner.add_args(["--timeout_iterations", "1000000000"])
        runner.add_args(["--timeout_seconds", str(200000)])
        runner.add_args(["--validator_must_support"])
        runner.add_args(self.extra_args)
        runner.add_args(["--generate_testcases"])
        runner.launch()
    def kill(self):
        self.runner.proc.kill()
    def finished(self):
        if not self.runner.finished():
            return False
        runner = self.runner
        
        #open("logs/"+str(self.i)+".stdout", "w").write(runner.get_file("stdout.out"))
        #open("logs/"+str(self.i)+".stderr", "w").write(runner.get_file("stderr.out"))
        j = runner.get_file("search.json")
        open("logs/"+str(self.i)+".json", "w").write(j if j is not None else "")
        
        if runner.successful():
            print "STOKE finished on", self.i
            r = json.loads(j)
            r = {'iters': r["statistics"]["total_iterations"],
                      'examples': r["statistics"]["total_counterexamples"],
                      'name': self.i,
                      'verified': r['verified']}
        else:
            print "STOKE Failed on", self.i
            print runner.get_file("stderr.out")
            r = {"name":self.i,"error":True}
        runner.cleanup()
        self.output_file.write(json.dumps(r,  separators=(',',':'), ensure_ascii=True)+"\n")
        self.output_file.flush()
        return True

def make_target(target):
    t = synth.SynthTarget()
    t.def_in = target.def_in
    t.live_out = filter(lambda x: x != "%af", target.live_out)
    t.target = ".f:\n" + "\n".join(target.instrs) +"\nretq\n"
    t.testcases = ""
    return t

def stoke_tasks(outfile, args):
    families = FamilyLoader("targets/libs.families")
    jobs = map(int,open("1000progs_filtered.txt").read().split("\n"))
    output_file = open(outfile, "w")
    for i in jobs:
        yield StokeTask(i, make_target(families[i].head), output_file, args)
    

arguments = {"walk": ["--no_relax_reg", "--cost", "correctness > 0", "--cycle_timeout", "10000000"],
             "hamming": ["--no_relax_reg", "--cost", "correctness", "--cycle_timeout", "10000000"],
             "misalign": ["--cost", "correctness", "--cycle_timeout", "10000000"],
             "exponential": ["--cost", "correctness","--cycle_timeout", "10000,20000,40000,80000,160000,320000,640000,1280000,2560000,5120000,10240000,20480000,40960000"],
             "gadgets": ["--cost", "correctness","--double_mass", "3", "--cycle_timeout", "10000,20000,40000,80000,160000,320000,640000,1280000,2560000,5120000"]
            }
def main():
    assert len(sys.argv) == 3
    outfile = sys.argv[1]
    kind = sys.argv[2]
    assert kind in arguments
    args = arguments[kind]
    run_tasks(stoke_tasks(outfile, args), 28)

main()
