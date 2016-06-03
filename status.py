import pg, sys, pgmq

def main():
    series_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    conn = pg.connect('jrkoenig')
    c = conn.cursor()
    if series_id is not None:
        c.execute("SELECT series, count(*) FROM distr_output WHERE series = %s;", [series_id])
    else:
        c.execute("SELECT distr_series.name, counts.num, counts.series FROM (SELECT series, count(*) as num FROM distr_output GROUP BY series) as counts INNER JOIN distr_series ON counts.series = distr_series.id ORDER BY series;")
    for (name, cnt, series) in c:
        sys.stdout.write("[{:d}]\tcompleted {:d}\t({})\n".format(series, cnt, name))
    s = pgmq.Server(conn, "synth_queue")
    (ip, pending) = s.get_counts()
    sys.stdout.write("Queue:\n in progress: {:d}, pending: {:d}\n".format(ip, pending))
    conn.close()
if __name__ == "__main__":
    main()
