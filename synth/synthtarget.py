
import StringIO, gzip, base64

class SynthTarget(object):
    def __init__(self):
        self._testcases_gz_base64 = ""
        self.target = ""
        self.live_out = []
        self.def_in = []
        self.use_mem = False
    def _set_testcases(self, testcases):
        if testcases == "":
            self._testcases_gz_base64 = ""
        else:
            stream = StringIO.StringIO()
            with gzip.GzipFile(fileobj = stream, mode = "w") as f:
              f.write(testcases)
            self._testcases_gz_base64 = base64.b64encode(stream.getvalue())
    def _get_testcases(self):
        if self._testcases_gz_base64 == "":
            return ""
        stream = StringIO.StringIO(base64.b64decode(self._testcases_gz_base64))
        with gzip.GzipFile(fileobj = stream, mode = "r") as f:
            return f.read()
    testcases = property(_get_testcases, _set_testcases, None, "Testcases")
    def to_json(self):
        return {'target': self.target,
                'liveout': self.live_out,
                'defin': self.def_in,
                'tc': self._testcases_gz_base64,
                'usemem': self.use_mem}
    @staticmethod
    def from_json(jsonobj):
        self = SynthTarget()
        self.target = jsonobj['target']
        self.live_out = jsonobj['liveout']
        self.def_in = jsonobj['defin']
        self._testcases_gz_base64 = jsonobj['tc']
        self.use_mem = jsonobj['usemem']
        return self
