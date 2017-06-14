
import json, sys
from synth.families import FamilyLoader
import synth

args = ["--cost", 'correctness', "--timeout_iterations", "10000000","--interrupt_after", str(60), "--validator_must_support","--generate_testcases"]
args += [#"--cost", "correctness",
"--reduction", "sum",
"--training_set", "{ ... }",
"--solver_timeout", "30000",
"--misalign_penalty", "3",
"--beta", "1.0",
"--distance", "hamming",
#"--strategy", "bounded",
"--strategy", "none",
#"--failed_verification_action", "add_counterexample",
"--failed_verification_action", "quit",
"--sig_penalty", "200",
"--cpu_flags", "{ cmov sse sse2 popcnt }"]

targets = []
for l in open("1000progs_filtered.txt"):
    try:
        targets.append(int(l.strip()))
    except ValueError:
        break
l = [{'target': targets[i%len(targets)], 'args': args+['--seed',str(i+1)]} for i in range(len(targets)*5)]

families = FamilyLoader("targets/libs.families")

def make_target(target):
    t = synth.SynthTarget()
    t.def_in = target.def_in
    t.live_out = filter(lambda x: x != "%af", target.live_out)
    t.target = ".f:\n" + "\n".join(target.instrs) +"\nretq\n"
    t.testcases = ""
    return t
    
jsonl = open("jobs.jsonl","w")
for i,j in enumerate(l):
    target = make_target(families[int(j['target'])].head).to_json()
    run_desc = {'run':str(j['target'])+"("+str(i)+")", 'args': j['args'], 'target': target, 'log_files': ['search.json']}
    
    #with open("data/config/"+str(i)+".json","w") as f:
    #    f.write(json.dumps(run_desc, indent=2))
    jsonl.write(json.dumps(run_desc,separators=(',',':'))+"\n")
    