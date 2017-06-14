
import httplib, time, random, json, urllib, socket
import synth, sys, os
from synth import stokerunner

STOKE_BIN = os.path.join(os.getenv("HOME"),"expt/stoke/bin/stoke_expt")

def flush_response(conn):
    resp = conn.getresponse()
    resp.read()

class StokeTask(object):
    def __init__(self, runner, finalizer):
        self.finalizer = finalizer
        self.runner = runner
    def kill(self):
        self.runner.proc.kill()
    def finished(self):
        if not self.runner.finished():
            return False
        self.finalizer(self.runner)
        return True

class Worker(object):
    def __init__(self, conn, hostname, max_tasks = 1):
        self.last_heartbeat = time.time()
        self.conn = conn
        self.max_tasks = max_tasks
        self.outstanding = []
        self.hostname = hostname
    def add_tasks(self, task_producer):
        while len(self.outstanding) < self.max_tasks:
            t = task_producer()
            if t is not None:
                self.outstanding.append(t)
            else:
                break
    def run(self):
        self.outstanding = [task for task in self.outstanding if not task.finished()]
    def cleanup(self):
        for o in self.outstanding:
            o.kill()
    def heartbeat(self):
        now = time.time()
        if now - self.last_heartbeat > 5:
            self.conn.request("POST", "/heartbeat?worker=" + self.hostname)
            flush_response(self.conn)
            self.last_heartbeat = now

def get_task_from_server(conn, hostname):
    conn.request("POST", "/task/get?worker=" + hostname)
    resp = conn.getresponse()
    data = resp.read()
    if resp.status == 204:
        return None
    elif resp.status == 200:
        task_desc = json.loads(data)
        run_desc = task_desc['run']
        state = None
        if task_desc['initial_state'] is not None:
            conn.request("GET", task_desc['initial_state'])
            resp = conn.getresponse()
            if resp.status != 200:
                print "failed to get initial_state from server"
                return None
            length = int(resp.getheader('content-length'))
            state = resp.read(length)
            if len(state) != length:
                print "Didn't get full file from server"
                return None
            
        runner = stokerunner.StokeRunner(STOKE_BIN)
        runner.setup(synth.SynthTarget.from_json(run_desc['target']), initial = None, state = state)
        runner.add_args(run_desc['args'])
        if task_desc['final_state']:
            runner.add_args(['--save_state', 'b.state'])
        runner.launch()
        def finalizer(runner):
            task_id = task_desc['id']
            j = runner.get_file("search.json")
            if runner.successful():
                print "STOKE finished on", task_id
                #print runner.get_file("stdout.out")
                r = json.loads(j)
            else:
                print "STOKE Failed on", task_id
                print runner.get_file("stderr.out")
                r = {"name": task_id,"error":True}
            print "uploading data"
            for log_file in run_desc['log_files']:
                data = runner.get_file(log_file)
                if data is not None:
                    print "sending", len(data), "bytes to", "/data/logs/"+str(task_id)+"/"+log_file
                    conn.request("POST","/data/logs/"+str(task_id)+"/"+log_file, data)
                    flush_response(conn)
            if task_desc['final_state'] is not None:
                data = runner.get_file('b.state')
                if data is not None:
                    conn.request("POST",task_desc['final_state'], data)
                    flush_response(conn)
            runner.cleanup()
            print "Finishing job"
            conn.request("POST", "/task/complete?" + urllib.urlencode({'worker': hostname, 'task': task_id}), json.dumps(r))
            flush_response(conn)
        return StokeTask(runner, finalizer)
    else:
        print "Invalid response from server to /task/get"
        print resp.status, resp.reason
        print data
        return None


def main():
    server_address = sys.argv[1] if len(sys.argv) > 1 else "localhost:8080"
    conn = httplib.HTTPConnection(server_address)
    threads = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    hostname = socket.gethostname() + "-{:06x}".format(random.randint(0,2**24))
    
    def get_task():
        return get_task_from_server(conn, hostname)
    
    worker = Worker(conn, hostname, threads)
    try:
        while True:
            worker.run()
            worker.heartbeat()
            worker.add_tasks(get_task)
            time.sleep(1)
    except KeyboardInterrupt:
        worker.cleanup()
main()
