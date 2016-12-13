
import subprocess, shutil, tempfile, os, io, gzip, time

class StokeRunner(object):
    def __init__(self, stoke_bin = 'stoke'):
        self.proc = None
        self.tdir = ''
        self.args = []
        self.stoke_bin = stoke_bin

    def setup(self, target, initial = None):
        assert target is not None
        try:
            self.tdir = tempfile.mkdtemp("-stoke-synth")
            def write_file(fn, contents):
                with open(os.path.join(self.tdir, fn), "w") as f:
                    f.write(contents)
            self.add_args(build_args(target))
            
            tc = target.testcases
            if tc != "":
                write_file("test.cases", target.testcases)
                self.add_args(["--testcases", "test.cases"])
            write_file("target.s", target.target)
            if initial is not None:
                write_file("initial.s", initial)
                self.add_args(['--init', 'previous','--previous', 'initial.s'])
            else:
                self.add_args(['--init', 'zero'])

        except:
            self.cleanup()
            raise
    def add_args(self, args):
        self.args.extend(args)
    def launch(self):
        assert self.tdir != ""

        stdout = open(os.path.join(self.tdir,"stdout.out"), "w")
        stderr = open(os.path.join(self.tdir,"stderr.out"), "w")
        self.proc = subprocess.Popen([self.stoke_bin, "search"] + self.args,
                                     cwd = self.tdir,
                                     stdout = stdout.fileno(),
                                     stderr = stderr.fileno())
        stdout.close()
        stderr.close()

    def wait(self):
        while not self.finished():
            time.sleep(1)
    def finished(self):
        return self.proc.poll() is not None
    def successful(self):
        return self.proc.poll() in [0,2]
    def get_file(self, fname):
        try:
            with open(os.path.join(self.tdir,fname), "r") as f:
                return f.read()
        except:
            return None
    def get_gz_file(self, fname):
        try:
            with open(os.path.join(self.tdir,fname), "r") as fstream:
                ostream = io.BytesIO()
                gstream = gzip.GzipFile(str(fname), "wb", 5, ostream)
                shutil.copyfileobj(fstream, gstream)
                gstream.close()
                return ostream.getvalue()
        except:
            raise
    def cleanup(self):
        try:
            if self.tdir != '':
                shutil.rmtree(self.tdir)
            self.tdir = ''
            self.proc = None
        except:
            pass


def _mk_set(l):
    return "{ " + " ".join(l) + (" }" if len(l) > 0 else "}")

def build_args(target):
    return [
      "--cpu_flags", "{ cmov sse sse2 popcnt }",
      "--target", "target.s",
      "--machine_output", "search.json",
      #"--cost", "correctness",
      "--reduction", "sum",
      "--training_set", "{ ... }",
      "--solver_timeout", "30000",
      "--misalign_penalty", "3",
      "--beta", "1.0",
      "--distance", "hamming",
      "--strategy", "bounded",
      "--failed_verification_action", "add_counterexample",
      "--sig_penalty", "200"] +\
      (["--def_in", _mk_set(target.def_in)] if target.def_in is not None else []) +\
      (["--live_out", _mk_set(target.live_out)] if target.live_out is not None else []) +\
      (["--heap_out"] if target.use_mem else [])
