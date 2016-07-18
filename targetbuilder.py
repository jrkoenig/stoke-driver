import synthtarget
import tempfile, shutil, os, json, subprocess, sys

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
              entry['use_mem'] = True if entry.get('use_mem', False) else False
              print "Compiling", entry['name']
              database[entry['name']] = _compile(entry, root)
    return database

def _compile(program_params, root):
    tdir = ''
    try:
        tdir = tempfile.mkdtemp("-stoke-synth")
        program = _J(tdir, "program")
        src_file = program_params['src_file']
        subprocess.check_call(["g++", "-std=c++11", "-O1", "-fno-inline", "-fomit-frame-pointer", "-fno-stack-protector",
                               src_file, "-o",  program], cwd=root)
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
        if 'live_out' in program_params:
            t.live_out = program_params['live_out']
        else:
            t.live_out = _LINUX_ABI_RESULTS[:program_params['retc']]+["%rsp"]
        if 'def_in' in program_params:
            t.def_in = program_params['def_in']
        else:
            t.def_in = _LINUX_ABI_ARGS[:program_params['argc']]+["%rsp"]
        t.use_mem = program_params['use_mem']
        return t
    finally:
        if tdir != '':
            shutil.rmtree(tdir)
            pass


def main():
    #gulwani = make_all_from_c("gulwani/gulwani.json")
    #small_benchmarks = make_all_from_c("benchmarks/database.json")
    bits = make_all_from_c("targets/src/bit/database.json")
    for name,target in bits.items():
        print name
        with open("targets/bit/"+name+".json", "w") as f:
            json.dump(target.to_json(), f)
"""

def main():
    if len(sys.argv) != 4:
        print "Usage: targetbuilder.py name path/to/target.s path/to/testcases.tc"
        return
    name = sys.argv[1]
    target = synthtarget.SynthTarget()
    target.target = _filecontents(sys.argv[2])
    if target.target is None:
        print "Could not open target file"
        return
    tcs = _filecontents(sys.argv[3])
    if tcs is None:
        print "Could not open testcases"
        return
    target.testcases = tcs
    target.use_mem = True
    target.live_out = None
    target.def_in = None
    with open(name+".json", "w") as f:
        json.dump(target.to_json(), f)

"""
if __name__ == "__main__":
    main()
