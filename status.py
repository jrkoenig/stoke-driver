import time, json, cgi
    
def tr(cells): return '<tr>'+''.join(map(lambda y: "<td>"+y+"</td>", cells))+"</tr>"
def E(s): return cgi.escape(s)

def overview(jobs):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
    r += ("<h1>Status</h1>")
    
    r += ("<h2>Jobs In Flight</h2>")
    j  = []
    for job, (server,desc) in jobs.inflight.items():
        if job in jobs.notstarted:
            j.append(tr([job, '', 'NotStarted']))
        else:
            j.append(tr([job, str(server), '<a href = "/status/job?job='+job+'">Processing</a>']))
    r += ("<table><th>Job</th><th>Server</th><th>Status</th>"+"\n".join(j)+"</table>")
    
    r += ("<h2>Jobs Completed</h2>")
    r += ("<p>Completed <a href=\"/status/completed\">"+str(len(jobs.completed))+"</a> jobs.</p>")
    
    r += ("<h2>Servers</h2>")
    now = time.time()
    servertimes = [tr([str(s), "{:.2f}</td>".format(now-last_seen)]) for s, last_seen in jobs.servers_last_seen.items()]
    r += ("<table><th>Server</th><th>Last Seen (sec)</th>"+"\n".join(servertimes)+"</table>")
    r += ("</body></html>")
    return r

def completed(jobs):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
    r += ("<h1>Completed</h1>")
    j = [tr(["<a href=\"/status/completed?job="+job+"\">" + job + "</a>"]) for job, res in sorted(jobs.completed.items())]
    r += ("<table><th>Job</th>"+"\n".join(j)+"</table>")
    r += ("</body></html>")
    return r

def result(jobs, j):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
    r += ("<h1>Results for "+j+"</h1>")
    pretty = json.dumps(jobs.completed[j], sort_keys=True, indent=2, separators=(',', ': '))
    r += ("<pre>"+E(pretty)+"</pre>")
    r += ("</body></html>")
    return r
    
def job(jobs, j):
    r = """<html><head><style>table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }</style></head><body>
        """
        
    server, desc = jobs.inflight[j]
    r += ("<h1>Setup for "+j+" on "+ server + "</h1>")
    pretty = json.dumps(desc, sort_keys=True, indent=2, separators=(',', ': '))
    r += ("<pre>"+E(pretty)+"</pre>")
    r += ("</body></html>")
    return r

