import synthtarget
import tempfile, shutil, os, json, subprocess

_J = os.path.join
_LINUX_ABI_ARGS = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
_LINUX_ABI_RESULTS = ["%rax"]
_FNULL = open(os.devnull, 'w')

def _filecontents(fname):
    try:
        with open(fname, "r") as f:
            return f.read()
    except:
        return None

def make_all_from_c(filename):
    root = os.path.split(filename)[0]
    abs_path = lambda rpath: os.path.abspath(os.path.join(root, rpath))
    database = {}
    with open(filename) as f:
        for entry in list(json.load(f)):
              entry['src'] = _filecontents(abs_path(entry['src_file']))
              entry['use_mem'] = True if entry.get('use_mem', False) else False
              database[entry['name']] = _compile(entry)
    return database

def _compile(program_params):
    tdir = ''
    try:
        tdir = tempfile.mkdtemp("-stoke-synth")
        program = _J(tdir, "program")
        src_file = _J(tdir, "main.cc")
        with open(src_file, "w") as f:
            f.write(program_params['src'])
            f.write('\n')
        subprocess.check_call(["g++", "-std=c++11", "-O1", "-fno-inline", "-fomit-frame-pointer",
                               src_file, "-o",  program])
        subprocess.check_call(["stoke", "extract", "--in",  program, "--out", _J(tdir,"bins")])
        subprocess.check_call(["stoke", "testcase", "--bin", program, "--out", _J(tdir, "tests.out"),
                               "--fxn", program_params['func'], "--max_testcases", "1000"],
                               stdout = _FNULL)
        tests_out = _filecontents(_J(tdir, "tests.out"))
        if tests_out is None or tests_out.strip() == '':
            sys.stderr.write('Error: no testcases produced!')
            raise RuntimeError

        func_s = _filecontents(_J(tdir, "bins", program_params['func']+".s"))
        if func_s is None or func_s.strip() == '':
            sys.stderr.write('Error: no func file!')
            raise RuntimeError

        t = synthtarget.SynthTarget()
        t.testcases = tests_out
        t.target = func_s
        t.live_out = _LINUX_ABI_RESULTS[:program_params['retc']]
        t.def_in = _LINUX_ABI_ARGS[:program_params['argc']]
        t.use_mem = program_params['use_mem']
        return t
    finally:
        if tdir != '':
            shutil.rmtree(tdir)
