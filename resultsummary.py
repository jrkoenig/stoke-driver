import pg
import json, math, sys, random

def first_order_stats(data):
    mean = sum([math.log(d) for d in data])/float(len(data))
    sd = (sum([(math.log(d) - mean)**2 for d in data])/float(len(data)-1))**0.5
    return math.exp(mean), math.exp(sd)

def mean(l):
    return sum(l)/float(len(l))
def median(l):
    a = sorted(l)
    if len(a) % 2 == 1:
        return a[len(a)/2]
    else:
        return (a[len(a)/2] + a[len(a)/2-1])*0.5

def get_iter_counts(conn, series):
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

def main():
    itercounts = {}
    MAX = 20000000

    conn = pg.connect('jrkoenig')
    get_iter_counts(conn, 2)
    
if __name__ == "__main__":
    main()
