
import sqlite3, json


def main():
    con = sqlite3.connect("job.sqlite")
    cur = con.cursor()
    cur.execute("CREATE TABLE `jobs` (\
        `job`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,\
        `config`	TEXT NOT NULL)")
    cur.execute("CREATE TABLE `notstarted` (\
        `job`	INTEGER NOT NULL UNIQUE,\
        FOREIGN KEY(`job`) REFERENCES `jobs.job`)")
    cur.execute("CREATE TABLE `running` (\
        `job`	INTEGER NOT NULL UNIQUE,\
        `server`	TEXT NOT NULL,\
        FOREIGN KEY(`job`) REFERENCES `jobs.job`)")
    
    args = ["--cost", 'correctness', "--timeout_iterations", "10000000","--timeout_seconds", str(60*60*24*2), "--validator_must_support","--generate_testcases"]
    targets = [229810,105886,197933,66217,227723,82322,147378]
    l = [json.dumps({'target': targets[i%len(targets)], 'args': args+['--seed',str(i+1)]}) for i in range(len(targets)*100)]
    
    for config in l:
        con.execute("INSERT INTO jobs (config) VALUES (?)", (config,))
    con.commit()
    
    con.close()
    
main()