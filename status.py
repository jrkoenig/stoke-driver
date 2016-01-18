import pg, sys, pgmq

def main():
    series_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    conn = pg.connect('jrkoenig')
    c = conn.cursor()
    if series_id is not None:
        c.execute("SELECT count(*) FROM distr_output WHERE series = %s;", [series_id])
        sys.stdout.write("Series {:d}, {:d} completed".format(series_id, c.fetchone()[0]))
    else:
        c.execute("SELECT series, count(*) as num FROM distr_output GROUP BY series ORDER BY series;")
        for (series, count) in c:
            sys.stdout.write("Series:"+str(series) + ", completed: " + str(count)+"\n")
    s = pgmq.Server(conn, "synth_queue")
    (ip, pending) = s.get_counts()
    sys.stdout.write("Queue:\n in progress: {:d}, pending: {:d}\n".format(ip, pending))
    conn.close()
if __name__ == "__main__":
    main()
