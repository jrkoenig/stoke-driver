import time, json, cgi
    
def tr(cells): return '<tr>'+''.join(map(lambda y: "<td>"+y+"</td>", cells))+"</tr>"
def E(s): return cgi.escape(str(s))

def overview(jobs):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
    r += ("<h1>Status</h1>")
    
    r += ("<h2>Tasks In Flight</h2>")
    j  = []
    for task, (worker,desc) in sorted(jobs.inflight.items()):
        if task in jobs.notstarted:
            j.append(tr([E(task), '', 'NotStarted']))
        else:
            j.append(tr([E(task), E(desc['run']['run']), E(worker), '<a href = "/status/task?task='+E(task)+'">Processing</a>']))
    r += ("<table><th>TaskID</th><th>Run</th><th>Worker</th><th>Status</th>"+"\n".join(j)+"</table>")
    
    #r += ("<h2>Jobs Completed</h2>")
    #r += ("<p>Completed <a href=\"/status/completed\">"+str(len(jobs.completed))+"</a> jobs.</p>")
    
    r += ("<h2>Workers</h2>")
    now = time.time()
    servertimes = [tr([str(s), "{:.2f}</td>".format(now-last_seen)]) for s, last_seen in jobs.servers_last_seen.items()]
    r += ("<table><th>Worker</th><th>Last Seen (sec ago)</th>"+"\n".join(servertimes)+"</table>")
    r += ("</body></html>")
    return r

def completed(jobs):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
    r += ("<h1>Completed</h1>")
    j = [tr(["<a href=\"/status/completed?job="+E(job)+"\">" + E(job) + "</a>"]) for job, res in sorted(jobs.completed.items())]
    r += ("<table><th>Job</th>"+"\n".join(j)+"</table>")
    r += ("</body></html>")
    return r

def task(jobs, tid):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
    if tid in jobs.inflight:
        worker, desc = jobs.inflight[tid]
        r += ("<h1>Setup for task "+E(tid)+" running on "+ worker + "</h1>")
        r += ("<p>Running from "+E(desc['info']['iters_so_far'])+" prior iterations.</p>")
        pretty = json.dumps(desc, sort_keys=True, indent=2, separators=(',', ': '))
        r += ("<pre>"+E(pretty)+"</pre>")
        r += ("</body></html>")
        return r
    elif tid in jobs.completed:
        results, desc = jobs.completed[tid]
        r += ("<h1>Results for task "+E(tid)+"</h1>")
        if results['success']:
            code = results['current']['code']
            iterations = results['statistics']['total_iterations']
            name = results['name']
            r += "<h3>Synthesized "+E(name)+" in "+E(iterations)+" iterations</h3>\n"
            r += "<code><pre style=\"background-color: #DDD\">"+E(code)+"</pre></code>\n"
        elif results['interrupted']:
            r += "<h3>Not finished after "+E(results['statistics']['total_iterations'])+" iterations</h3>\n"
        pretty = json.dumps(results, sort_keys=True, indent=2, separators=(',', ': '))
        r += ("<pre>"+E(pretty)+"</pre>")
        r += ("</body></html>")
        return r
    else:
        r += ("<h1>"+E(tid)+" not found</h1>")
        
