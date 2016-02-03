import threading
import os
import signal

_printlock = threading.Lock()
def _print(x):
    with _printlock:
        print x

class _Task(object):
    def __init__(self, func, args):
        self.func = func
        self.args = args
        self.worklist = range(0, len(args))
        self.worklock = threading.Lock()
        self.results = [None] * len(args)
    def get(self):
        with self.worklock:
            if len(self.worklist) == 0: return None
            else:
                return self.worklist.pop()
def _worker(task):
    while True:
        index = task.get()
        if index is not None:
            task.results[index] = task.func(task.args[index])
        else:
            return

def abort_handler(signum, frame):
    print 'Aborting...'
    os._exit(1)

def pmap(func, args, NUM_WORKERS = 8):
    workers = []
    task = _Task(func, list(reversed(args)))
    for i in range(NUM_WORKERS):
        t = threading.Thread(target = _worker, args = (task,))
        workers.append(t)
        t.start()
    signal.signal(signal.SIGINT, abort_handler)
    #wait for workers to finish
    for t in workers:
        while t.isAlive():
            t.join(1)
    return task.results
