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
    for l in open("results.jsonl"):
        j = json.loads(l)
        if (j['elapsed'] > 5):
            print j['iters']/j['elapsed']

if __name__ == "__main__":
    main()
