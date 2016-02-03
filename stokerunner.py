
import subprocess, shutil, tempfile, os

class StokeRunner(object):
    def __init__(self, stoke_bin = 'stoke'):
        self.proc = None
        self.tdir = ''
        self.args = []
        self.stoke_bin = stoke_bin

    def setup(self, target):
        assert target is not None
        try:
            self.tdir = tempfile.mkdtemp("-stoke-synth")
            def write_file(fn, contents):
                with open(os.path.join(self.tdir, fn), "w") as f:
                    f.write(contents)
            write_file("test.cases", target.testcases)
            write_file("target.s", target.target)
            self.add_args(build_args(target))

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
        return self.proc.wait()
    def finished(self):
        return self.proc.poll() is not None
    def successful(self):
        return self.proc.poll() in [0,1]
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
            gstream = gzip.GzipFile(str(f), "wb", 9, ostream)
            shutil.copyfileobj(fstream, gstream)
            gstream.close()
            return ostream.value()
        except:
            return None
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
      "--init", "zero",
      "--testcases", "test.cases",
      "--training_set", "{ ... }",
      "--target", "target.s",
      "--out", "out.s",
      "--initial_instruction_number", "32",
      "--machine_output", "search.json",
      "--failed_verification_action", "quit",
      "--strategy", "none",
      "--cost", "correctness",
      "--reduction", "sum",
      "--misalign_penalty", "3",
      "--beta", "1",
      "--seed", "0",
      "--distance", "hamming",
      "--sig_penalty", "100",
      "--def_in", _mk_set(target.def_in),
      "--live_out", _mk_set(target.live_out)]
