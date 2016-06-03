import pg, targetbuilder, tempfile
import json, math, sys, random, subprocess, os

def get_rewrites_server(conn, series):
    rewrites = {}
    c = conn.cursor()
    c.execute("SELECT result_json FROM distr_output WHERE series = %s", [series])
    for (l,) in c:
        result = json.loads(str(l.strip()), 'utf-8')
        n = result["name"]
        code = result["asm"]
        if result['correct']:
            if n in rewrites:
                rewrites[n].append(code)
            else:
                rewrites[n] = [code]
    conn.commit()
    return rewrites
def write_file(str):
    (f, fname) = tempfile.mkstemp('.s')
    f = os.fdopen(f, "w")
    f.write(str)
    f.close()
    return fname

def _mk_set(l):
    return "{ " + " ".join(l) + (" }" if len(l) > 0 else "}")
    
def main():
    devnull = open("/dev/null","w")
    targets = targetbuilder.make_all_from_c("gulwani/gulwani.json")
    rewrites = get_rewrites_server(pg.connect("jrkoenig"), int(sys.argv[1]))
    counts = {}
    results = []
    for name,codes in sorted(rewrites.items()):
        counts[name] = [0,0,0]
        for code in codes:
            t = None
            s = None
            r = None
            out = None
            try:
                target = targets[name]
                t = write_file(target.target)
                (_,s) = tempfile.mkstemp('.s')
                (_2,out) = tempfile.mkstemp('.txt')
                os.close(_)
                os.close(_2)
                r = write_file(code)
                subprocess.check_call(['stoke', 'debug', 'simplify', '--output', s, '--target', r, '--def_in', _mk_set(target.def_in), '--live_out', _mk_set(target.live_out)],     stdout = devnull.fileno())#, stderr = devnull.fileno())
                subprocess.call(['stoke', 'debug', 'verify', '--solver_timeout', '30000', '--machine_output', out, '--strategy', 'ddec', '--target', t, '--rewrite', s, '--def_in', _mk_set(target.def_in), '--live_out', _mk_set(target.live_out)], stdout = devnull.fileno(), stderr = devnull.fileno())
                result = json.loads(open(out).read())
                if result['error'] and result['error'] != '':
                    counts[name][0] += 1
                elif result['verified']:
                    counts[name][1] += 1
                else:
                    counts[name][2] += 1
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
        print name,",", c[0],",", c[1],",", c[2]
    print "name,error,verified,incorrect"
    for name, c in sorted(counts.items()):
        print name,",", c[0],",", c[1],",", c[2]
    json.dump(results, open("verifications.json", "w"), indent=4)
if __name__ == "__main__":
    main()
