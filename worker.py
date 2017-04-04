
import httplib, time, random, json, urllib, socket
import cPickle,synth, sys
from synth import stokerunner
from synth.families import FamilyLoader


def make_target(target):
    t = synth.SynthTarget()
    t.def_in = target.def_in
    t.live_out = filter(lambda x: x != "%af", target.live_out)
    t.target = ".f:\n" + "\n".join(target.instrs) +"\nretq\n"
    t.testcases = ""
    return t

class StokeTask(object):
    def __init__(self, i, families, desc):
        self.i = i
        self.target = make_target(families[int(desc['target'])].head)
        self.extra_args = desc.get('args', [])
    def start(self):
        self.runner = stokerunner.StokeRunner()
        runner = self.runner
        runner.setup(self.target, None)
        runner.add_args(self.extra_args)
        runner.launch()
    def kill(self):
        self.runner.proc.kill()
    def finished(self):
        if not self.runner.finished():
            return False
        runner = self.runner
        j = runner.get_file("search.json")
        if runner.successful():
            print "STOKE finished on", self.i
            r = json.loads(j)
        else:
            print "STOKE Failed on", self.i
            print runner.get_file("stderr.out")
            r = {"name":self.i,"error":True}
        runner.cleanup()
        conn.request("POST", "/job/complete?" + urllib.urlencode({'server': hostname, 'job': self.i}), json.dumps(r))
        conn.getresponse()
        return True

def run_tasks(task_producer, max_tasks = 2):
    outstanding = []
    last_heartbeat = 0
    try:
        have_more = True
        while have_more or len(outstanding) > 0:
            while have_more and len(outstanding) < max_tasks:
                try:
                    t = next(task_producer)
                    if t is not None:
                        t.start()
                        outstanding.append(t)
                    else:
                        break
                except StopIteration:
                    have_more = False
            time.sleep(0.1)
            
            outstanding = filter(lambda t: not t.finished(), outstanding)
            now = time.time()
            if now - last_heartbeat > 5:
                conn.request("POST", "/heartbeat?server="+hostname)
                resp = conn.getresponse()
                last_heartbeat = now
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        for o in outstanding:
            o.kill()

def stoke_tasks():
    families = FamilyLoader("targets/libs.families")
    last_empty = time.time()
    wait = 0
    while True:
        if time.time() - last_empty < wait:
            yield None
        else:
            conn.request("POST", "/job/get?server="+hostname)
            resp = conn.getresponse()
            if resp.status != 200:
                print "Error from server"
            else:
                jobs = json.loads(resp.read())
                if len(jobs) == 0:
                    last_empty = time.time()
                    wait = random.uniform(5,20)
                    yield None
                else:
                    (name, desc) = jobs[0]
                    yield StokeTask(name, families, desc)
    
def main():
    global hostname, conn
    hostname = socket.gethostname()
    if len(sys.argv) > 1:
        conn = httplib.HTTPConnection(sys.argv[1])
    else:
        conn = httplib.HTTPConnection("localhost:8080")
    if len(sys.argv) > 2:
        threads = int(sys.argv[2])
    else:
        threads = 1
    hostname += "-{:x}".format(random.randint(0,2**24))
    run_tasks(stoke_tasks(), threads)

main()
