
import threading, sys, urlparse, time, json, os, urllib, posixpath, shutil, errno
import status
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    
class JobManager(object):
    def __init__(self, source):
        self.source = source
        self.n = 0
        self.task_id = 0
        self.inflight = {}
        self.notstarted = set()
        self.log = open("results.jsonl", "w")
        self.completed = {}
        self.servers_last_seen = {}
        self.lock = threading.Lock()
        self.last_seen_lock = threading.Lock()

    def save(self,f):
        state = {'n':self.n, 'inflight': self.inflight, 'notstarted': list(self.notstarted)}
        f.write(json.dumps(state))
    def load(self,f):
        state = json.loads(f.read())
        self.n = state['n']
        for i in range(self.n):
            x = next(self.source)
        for k,v in state['inflight']:
            self.inflight[int(k)] = (v[0],v[1])
        self.notstarted = set(state['notstarted'])
    def mark_alive(self, server):
        with self.last_seen_lock:
            self.servers_last_seen[server] = time.time()
    def get_from_source(self):
        try:
            nx = next(self.source)
            self.n += 1
            return nx
        except StopIteration:
            return None
    def get(self, s):
        with self.lock:
            if len(self.notstarted) > 0:
                task_desc = self.inflight[self.notstarted.pop()][1]
            else:
                run_desc = self.get_from_source()
                if run_desc is None:
                    return None
                tid = self.task_id
                self.task_id += 1
                info = {"prior": None, 'iters_so_far': 0}
                task_desc = {"id": tid, "run": run_desc, 'info':info, "initial_state": None, "final_state": "/data/states/"+str(tid)+"/final.state"}
            self.inflight[task_desc['id']] = (s, task_desc)
            return task_desc
    def complete(self, job, result):
        with self.lock:
            if job in self.inflight:
                if result['interrupted']:
                    old_task = self.inflight[job][1]
                    tid = self.task_id
                    self.task_id += 1
                    print "continuing", old_task['id'], "with", tid
                    info = {"prior": old_task['id'], 'iters_so_far': result['statistics']['total_iterations']}
                    task_desc = {"id": tid, "run": old_task['run'],"info":info, "initial_state": old_task['final_state'], "final_state": "/data/states/"+str(tid)+"/final.state"}
                    self.inflight[task_desc['id']] = (None, task_desc)
                    self.notstarted.add(task_desc['id'])
                else:
                    print "completed", self.inflight[job][1]['run']['run'], "on task", job, "in", result['statistics']['total_iterations']
                    name = self.inflight[job][1]['run']['run']
                    result['name'] = name
                    self.log.write(json.dumps(result)+"\n")
                    self.log.flush()
                self.completed[job] = (result, self.inflight[job][1])
                del self.inflight[job]
                print "completed" , job
                return True
            else:
                print "couldn't find job", job
                return False
    def sync(self):
        with self.lock:
            self.save(open("state.json","w"))
        with self.last_seen_lock:
            now = time.time()
            timeout = 60
            alive_servers = set([server for server, last_seen in self.servers_last_seen.items() if last_seen > now - timeout])
            with self.lock:
                for job, (server, d) in self.inflight.items():
                    if job not in self.notstarted and server not in alive_servers:
                        self.notstarted.add(job)
            dead_servers = set(self.servers_last_seen.keys()) - alive_servers
            for server in dead_servers:
                del self.servers_last_seen[server]

jobs = None

def heartbeat(req, path, query):
    jobs.mark_alive(query['worker'][0])
    req.send_response(200)

def send_string(req, string):
    req.send_response(200)
    req.send_header('content-length', len(string))
    req.end_headers()
    req.wfile.write(string)

def getjob(req, path, query):
    rserver = query['worker'][0]
    n = jobs.get(rserver)
    if n is not None:
        send_string(req, json.dumps(n))
    else:
        req.send_response(204)
        req.end_headers()

def completetask(req, path, query):
    job = int(query['task'][0])
    result = json.loads(req.rfile.read(int(req.headers.getheader('content-length'))))
    if jobs.complete(job, result):
        req.send_response(200)
    else:
        req.send_response(500)

def statusoverview(req, path, query):
    send_string(req, status.overview(jobs))
def statustask(req, path, query):
    task = int(query['task'][0])
    send_string(req, status.task(jobs, task))

posthandlers = {'/heartbeat': heartbeat,
                '/task/get': getjob,
                '/task/complete': completetask}
gethandlers = {'/status/overview': statusoverview,
               '/': statusoverview,
               '/status/task': statustask}
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
def translate(path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath("./"+urllib.unquote(path))
        print "translated path", path
        return path
        
def handle_file_GET(self):
        fn = translate(self.path)
        try:
            if fn is None:
                raise IOError()
            f = open(fn, "rb")
            fs = os.fstat(f.fileno())
        except IOError:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Length", str(fs[6]))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
        
def handle_file_POST(self):
        fn = translate(self.path)
        if fn is None:
            self.send_response(400)
            self.end_headers()
            return
        dirs, name = os.path.split(fn)
        size = int(self.headers['content-length'])
        data = self.rfile.read(size)
        if len(data) == size:
            try:
                mkdir_p(dirs)
                f = open(fn, "wb")
                f.write(data)
                f.close()
                self.send_response(200)
                self.end_headers()
            except IOError:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()
class GetHandler(BaseHTTPRequestHandler):
    def do(self, handlers):
        parsed_path = urlparse.urlparse(self.path)
        querydict = urlparse.parse_qs(parsed_path.query)
        path = parsed_path.path
        if path in handlers:
            handlers[path](self, path, querydict)
        else:
            self.send_response(404)
    def do_GET(self):
        if self.path.startswith("/data/"):
            handle_file_GET(self)
        else:
            self.do(gethandlers)
    def do_POST(self):
        if self.path.startswith("/data/"):
            handle_file_POST(self)
        else:
            self.do(posthandlers)
        
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main():
    global jobs
    jobs = JobManager(json.loads(l) for l in open("jobs.jsonl","r"))
    port = 8080 if len(sys.argv) <= 1 else int(sys.argv[1])
    server = ThreadedHTTPServer(('', port), GetHandler)
    thread = threading.Thread(target = lambda: server.serve_forever())
    if not os.path.isdir("./data"):
        os.mkdir("data")
    try:
        jobs = JobManager(json.loads(l) for l in open("jobs.jsonl","r"))
        jobs.load(open("state.json"))
    except:
        jobs = JobManager(json.loads(l) for l in open("jobs.jsonl","r"))
    thread.start()
    print 'Starting server, use <Ctrl-C> to stop'
    try:
        while True:
            jobs.sync()
            time.sleep(30)
    except KeyboardInterrupt:
        pass
    server.shutdown()
            
if __name__ == '__main__':
    main()