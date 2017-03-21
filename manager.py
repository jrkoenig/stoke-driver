
args = ["--cost", 'correctness', "--timeout_iterations", "10000000","--timeout_seconds", str(60*60*24*2), "--validator_must_support","--generate_testcases"]
targets = [229810,105886,197933,66217,227723,82322,147378]

class JobSource(object):
    def __init__(self):
        self.l = [("{:06d}".format(i), {'target': targets[3], 'args': args+['--seed',str(i)]}) for i in range(7)]
    def pop(self):
        n = self.l[0]
        self.l = self.l[1:]
        return n
    def __len__(self):
        return len(self.l)

import threading
import status
import sys


class JobManager(object):
    def __init__(self, ):
        self.servers_last_seen = {}
        self.inflight = {}
        self.notstarted = set()
        self.completed = {}
        self.source = JobSource()
        self.lock = threading.Lock()

    def mark_alive(self, server):
        with self.lock:
            self.servers_last_seen[server] = time.time()
    def get(self, s):
        with self.lock:
            if len(self.notstarted) > 0:
                n = self.notstarted.pop()
                d = self.inflight[n][1]
            elif len(self.source) > 0:
                n, d = self.source.pop()
            else:
                return []
            self.inflight[n] = (s, d)
            return [(n,d)]
    def complete(self, job, result):
        with self.lock:
            if job in self.inflight:
                del self.inflight[job]
                self.completed[job] = result
                print "completed" , job
                return True
            else:
                print "couldn't find job", job
                return False
    def cleanup(self):
        with self.lock:
            now = time.time()
            timeout = 60
            dead_servers = set([server for server, last_seen in self.servers_last_seen.items() if last_seen < now - timeout])
            if len(dead_servers) > 0:
                print "Lost servers", dead_servers
                for job, (server, d) in self.inflight.items():
                    if job not in self.notstarted and server in dead_servers:
                        self.notstarted.add(job)
                for server in dead_servers:
                    del self.servers_last_seen[server]

jobs = JobManager()

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse, time, json

def heartbeat(req, path, query):
    jobs.mark_alive(query['server'][0])
    req.send_response(200)

def send_string(req, string):
    req.send_response(200)
    req.send_header('content-length', len(string))
    req.end_headers()
    req.wfile.write(string)

def getjob(req, path, query):
    rserver = query['server'][0]
    jobs.mark_alive(rserver)
    nextjobs = jobs.get(rserver)
    send_string(req, json.dumps(nextjobs))

def completejob(req, path, query):
    server = query['server'][0]
    job = query['job'][0]
    jobs.mark_alive(server)
    result = json.loads(req.rfile.read(int(req.headers.getheader('content-length'))))
    if jobs.complete(job, result):
        req.send_response(200)
    else:
        req.send_response(500)

def statusoverview(req, path, query):
    send_string(req, status.overview(jobs))
def statusjob(req, path, query):
    job = query['job'][0]
    send_string(req, status.job(jobs, job))
def statuscompleted(req, path, query):
    if 'job' in query:
        r = status.result(jobs, query['job'][0])
    else:
        r = status.completed(jobs)
    send_string(req, r)

posthandlers = {'/heartbeat': heartbeat,
                '/job/get': getjob,
                '/job/complete': completejob}
gethandlers = {'/status/overview': statusoverview,
               '/': statusoverview,
               '/status/completed': statuscompleted,
               '/status/job': statusjob}

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
        self.do(gethandlers)
    def do_POST(self):
        self.do(posthandlers)
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def cleanup():
    while True:
        time.sleep(5)
        jobs.cleanup()
if __name__ == '__main__':
    port = 8080 if len(sys.argv) <= 1 else int(sys.argv[1])
    server = ThreadedHTTPServer(('', port), GetHandler)
    thread = threading.Thread(target = cleanup)
    thread.start()
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
    sys.exit(1)
