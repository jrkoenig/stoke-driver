
import json, math, sys, random
import expsim
from collections import defaultdict

# values are the samples, bins are the lower bounds of each bin (must be sorted)
def histogram(values, bins):
    counts = [0] * len(bins)
    for v in values:
        i = -1
        for lowerbound in bins:
            if v is None or v >= lowerbound: i += 1
            else: break
        if i != -1: counts[i] += 1
        else: raise RuntimeError # value is smaller than all bins
    return counts

def find_exp_bins(values, divisions_per_decade = 5):
    l = float("+inf")
    h = 0.0
    
    for v in values:
        if v < 1 or math.isinf(v): continue
        lv = math.log10(float(v))
        l = min(lv,l)
        h = max(h, lv)
    
    assert l <= h
    
    smallest = math.floor(l*divisions_per_decade)
    largest = math.ceil(h*divisions_per_decade)
    return [math.pow(10, (smallest+i)/divisions_per_decade) for i in range(int(largest-smallest))]
    
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

def get_iter_counts_jsonl(fname):
    
    itercounts = {}
    for l in open(fname):
        result = json.loads(str(l.strip()), 'utf-8')
        n = result["name"]
        i = int(result["iters"]) if result["success"] else None
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

def main():

    arg = sys.argv[1]
    MAX = 5000000
    itercounts = get_iter_counts_jsonl(arg)
    exp_scheme = lambda st: expsim.exponential(st, k = 2.0, T_0=100000)
    sizes = defaultdict(list)
    size_counts = defaultdict(lambda: 0)
    for i in sorted(itercounts.keys()):
        size = int(i.split("-")[1])
	sizes[size].extend(itercounts[i])
        size_counts[size] += len([t for t in itercounts[i] if t is None or t > 0])
        #sim = make_stoke_sim(itercounts[i], MAX)
        #ET = expsim.run_stoke_sim(sim, exp_scheme)
        #if len(itercounts[i]) > 4:
        #    print i, ET
        #sizes[size].append(ET)
    bins = [0]+find_exp_bins([100,8000000],5)
    print "name,"+",".join(map(str, bins))
    for size in sorted(sizes.keys()):
        print size,
        filtered = [ic for ic in sizes[size] if ic is not None and ic > 0]
        counts = histogram(filtered, bins)
        print ","+",".join(map(lambda x: str(float(x)/size_counts[size]), counts))
    print size_counts

if __name__ == "__main__":
    main()
