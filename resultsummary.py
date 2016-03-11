import pg
import json, math, sys, random
import expsim

def first_order_stats(data):
    mean = sum([math.log(d) for d in data])/float(len(data))
    sd = (sum([(math.log(d) - mean)**2 for d in data])/float(len(data)-1))**0.5
    return math.exp(mean), math.exp(sd)

def log_order_stats(data):
    mean = sum([math.log(d) for d in data])/float(len(data))
    sd = (sum([(math.log(d) - mean)**2 for d in data])/float(len(data)-1))**0.5
    return mean, sd

def mean(l):
    return sum(l)/float(len(l))
def median(l):
    a = sorted(l)
    if len(a) % 2 == 1:
        return a[len(a)/2]
    else:
        return (a[len(a)/2] + a[len(a)/2-1])*0.5

def get_iter_counts_server(conn, series):
    itercounts = {}
    c = conn.cursor()
    c.execute("SELECT result_json FROM distr_output WHERE series = %s",[series])
    for (l,) in c:
        result = json.loads(str(l.strip()), 'utf-8')
        n = result["name"]
        i = int(result["iters"]) if result["correct"] else None
        if n in itercounts:
            itercounts[n].append(i)
        else:
            itercounts[n] = [i]
    conn.commit()
    return itercounts

def get_iter_counts_jsonl(fname):
    itercounts = {}
    for l in open(fname):
        result = json.loads(str(l.strip()), 'utf-8')
        n = result["name"]
        i = int(result["iters"]) if result["correct"] else None
        if n in itercounts:
            itercounts[n].append(i)
        else:
            itercounts[n] = [i]
    return itercounts
    
def make_stoke_sim(timings, limit):
    times = [t for t in timings if t is not None and t < limit]
    nruns = len(timings)
    return expsim.StokeSim(times, nruns)
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        
def get_iter_counts(s):
    if s.endswith(".jsonl"):
        return get_iter_counts_jsonl(s)
    elif is_int(s):
        return get_iter_counts_server(pg.connect("jrkoenig"), int(s))
    else:
        return {}
def main():
    args = sys.argv[1:]
    MAX = 20000000
    itercounts = [get_iter_counts(s) for s in args]
    exp_scheme = lambda st: expsim.exponential(st, k = 2.0, T_0=100000)
    keys = set()
    for ic in itercounts: keys.update(ic.keys())
    
    print ",".join(["name"] + [str(a) for a in args])
    for i in sorted(keys):
        print str(i)+",",
        for ic in itercounts:
            if i in ic:
                sim = make_stoke_sim(ic[i], MAX)
                ET = expsim.run_stoke_sim(sim, exp_scheme)
                print str(ET)+",",
            else:
                print ",",
        print ""

if __name__ == "__main__":
    main()
