
import math

class Done(Exception):
    pass

class StokeSim(object):
    def __init__(self, times, total_runs):
        self.reset()
        self.cdf = sorted(times)
        self.norm = float(total_runs)
    def reset(self):
        self.residual_pr = 1.0
        self.expected_iters = 0.0
        self.total_count = 0
    def sim(self, timeout):
        if len(self.cdf) == 0 or timeout >= self.cdf[-1]:
            i = len(self.cdf)
        else:
            l, h = 0, len(self.cdf)
            while(h-l>1):
                m = l + (h-l)/2
                if timeout >= self.cdf[m]:
                    l = m
                else:
                    h = m
            i = l
        pr = i / self.norm
        e = sum(self.cdf[:i])/i if i > 0 else timeout
        return (float(pr), float(e))
    def run(self, timeout):
        (pr_success, expected_iters) = self.sim(timeout)
        self.expected_iters += self.residual_pr * expected_iters
        self.residual_pr = self.residual_pr * (1 - pr_success)
        self.total_count += 1
        if self.residual_pr < 0.0001 or self.total_count >= 100000: raise Done
    def timedout(self):
        return self.total_count == 100000
    def expected(self):
        return self.expected_iters

def simple(st, T = 10000):
    while True:
        st.run(T)
def exponential(st, k = 1.1, T_0 = 50000):
    T = T_0
    while True:
        st.run(T)
        T = k*T

def run_stoke_sim(st, f):
    st.reset()
    try:
        f(st)
        raise RuntimeError
    except Done:
        if st.timedout(): return float('Inf')
        return st.expected()
