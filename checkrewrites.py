import synth, tempfile, pickle
import json, math, sys, random, subprocess, os

def write_file(str):
    (f, fname) = tempfile.mkstemp('.s')
    f = os.fdopen(f, "w")
    f.write(str)
    f.close()
    return fname

def _mk_set(l):
    return "{ " + " ".join(l) + (" }" if len(l) > 0 else "}")

class Target(object):
    def __init__(self, di, lo, instrs):
        self.def_in = di
        self.live_out = lo
        self.instrs = instrs
    def __str__(self):
        return "(" + ",".join(self.def_in) +")->("+",".join(self.live_out)+") {" + "; ".join(self.instrs) + "}"
    def size(self): return len(instrs)

class Family(object):
    def __init__(self, target):
        self.head = target
        self.rest = []
    def __str__(self):
        return str(self.head) + " & " + ",".join(map(str,self.rest))
    def merge_if_contained(self, target):
        if self.head.def_in != target.def_in:
            return False
        s = len(self.head.instrs)
        if s == len(target.instrs) and self.head.instrs == target.instrs:
            # target is the same as head. ignore so we don't get duplicates
            return True
        elif s < len(target.instrs) and self.head.instrs == target.instrs[:s]:
            self.rest.append((s,self.head.live_out))
            self.head = target
            return True
        elif s > len(target.instrs) and target.instrs == self.head.instrs[:len(target.instrs)]:
            self.rest.append((len(target.instrs), target.live_out))
            self.rest.sort(key = lambda x: x[0])
            return True
        else:
            return False

def write_counts(counts):
    f = open("verification_results.csv", "w")
    f.write("name,errors,verified,counterexamples,otherwise\n")
    for name, c in sorted(counts.items()):
        f.write(name+","+str(c[0])+","+str(c[1])+","+str(c[2])+","+str(c[3])+"\n")
    f.close()
 
def main():
    devnull = open("/dev/null","w")
    families = pickle.load(open("libs.families.pickle", "r"))
    counts = {}
    results = []
    iters = 0
    for l in open("a.jsonl"):
        if l.strip() == "": continue
        j = json.loads(l)
        name = j['name'].split("-")[0]
        if not j['success']:
            continue
        if name not in counts:
            counts[name] = [0,0,0,0]
        code = j['code']
        t = None
        s = None
        r = None
        out = None
        try:
            target = families[int(name)].head
            t = write_file(".f:\n"+"\n".join(target.instrs)+"\nretq\n")
            (s_fd,s) = tempfile.mkstemp('.s')
            (txt_fd,out) = tempfile.mkstemp('.txt')
            os.close(txt_fd)
            os.close(s_fd)
            r = write_file(code)
            target.live_out = filter(lambda x: x!="%af",target.live_out)
            simplified_output = subprocess.check_output(['stoke', 'debug', 'simplify', '--target', r, '--def_in', _mk_set(target.def_in), '--live_out', _mk_set(target.live_out)])#, stderr = devnull.fileno())
            s_lines = None
            for l in simplified_output.split("\n"):
                if l == "Simplified program:":
                    s_lines = []
                elif s_lines is not None:
                    s_lines.append(l)  
            simplified = "\n".join(s_lines)
            open(s,"w").write(simplified)
            
            subprocess.call(['stoke', 'debug', 'verify', '--solver_timeout', '30000', '--machine_output', out, '--strategy', 'bounded', '--target', t, '--rewrite', s, '--def_in', _mk_set(target.def_in), '--live_out', _mk_set(target.live_out)], stdout = devnull.fileno())#, stderr = devnull.fileno())

            result = json.loads(open(out).read())
            if result['error'] and result['error'] != '':
		print "Error", name, "->", result['error']
                counts[name][0] += 1
            elif result['verified']:
                counts[name][1] += 1
            elif result['counter_examples_available']:
		counts[name][2] += 1
            else:
                counts[name][3] += 1
            result['name'] = name
            result['code'] = code
            results.append(result)
            os.remove(t)
            os.remove(s)
            os.remove(r)
            os.remove(out)
        except Exception as e:
            if t:
                os.remove(t)
            if s:
                os.remove(s)
            if r:
                os.remove(r)
            if out:
                os.remove(out)
            raise e
        c = counts[name]
        #print name,",", c[0],",", c[1],",", c[2]
        
        iters += 1
        if iters % 50 == 1:
            write_counts(counts)
    write_counts(counts)
    json.dump(results, open("verifications.json", "w"), indent=4)
if __name__ == "__main__":
    main()
