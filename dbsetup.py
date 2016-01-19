
import pg, pgmq

def setup():
    conn = pg.connect('jrkoenig')
    s = pgmq.Server(conn, "synth_queue")
    s.recreate()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS distr_output CASCADE;")
    c.execute("DROP TABLE IF EXISTS distr_series CASCADE;")
    c.execute("DROP TABLE IF EXISTS distr_gz_captures CASCADE;")
    c.execute("CREATE TABLE distr_series (id bigserial PRIMARY KEY,\
                                          name varchar(1000),\
                                          stoke_hash varchar(100));")
    c.execute("CREATE TABLE distr_output (id bigserial PRIMARY KEY,\
                                          series bigint REFERENCES distr_series(id),\
                                          result_json text);")
    c.execute("CREATE TABLE distr_gz_captures (id bigserial PRIMARY KEY,\
                                               output bigint REFERENCES distr_output(id),\
                                               file varchar(1000),\
                                               data bytea);")
    s.conn.commit()

if __name__ == "__main__":
    print "This operation will clear all data and cannot be undone."
    response = raw_input("Are you sure you want to recreate the database? [y/N] ").lower()
    if response in ['y', 'yes']:
        print "Recreating..."
        setup()
        print "Done."
    elif response in ['n', 'no'] or response == '':
        print "No changes made."
    else:
        print "Please type 'y', 'yes', 'n', or 'no'. Aborting."
