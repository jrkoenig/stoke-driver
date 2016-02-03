
import pg, socket, os, select, re

class Message(object):
    def __init__(self, server, data, rowid):
        self._server = server
        self._data = data
        self._rowid = rowid
    def data(self):
        return self._data
    def finish(self):
        self._server._ack_message(self._rowid)
    def abort(self):
        self._server._unack_message(self._rowid)
class Server(object):
    def __init__(self, db, channel = "default"):
        if re.match("^[a-zA-Z0-9_]*$", channel) is None:
            raise RuntimeException("Channel name must be an "+
                                   "alphanumeric/underscore identifier")
        self.conn = db
        self._cursor = self.conn.cursor()
        self.channel = channel
        self._host = socket.gethostname()
        self._pid = os.getpid()
    def recreate(self):
        c = self._cursor
        c.execute("DROP TABLE IF EXISTS messages_"+self.channel+";")
        c.execute("CREATE TABLE messages_"+self.channel+"\
                     (id bigserial PRIMARY KEY,\
                      inprogress boolean NOT NULL,\
                      submit_time timestamp NOT NULL,\
                      data bytea NOT NULL,\
                      host varchar(1000),\
                      pid int);")
        c.execute("CREATE INDEX messages_index_"+self.channel
                 +" ON messages_"+self.channel+" (inprogress, id) \
                 WHERE inprogress is false;")
        self.conn.commit()
    def get_counts(self):
        self._cursor.execute("SELECT inprogress, COUNT(*) AS c FROM messages_"+self.channel+"\
                              GROUP BY inprogress;", [])
        count_inprogress, count_pending = (0,0)
        for (inprogress, c) in self._cursor:
            if inprogress:
                count_inprogress = c
            else:
                count_pending = c
        return (count_inprogress, count_pending)

    def post(self, data):
        self._cursor.execute("INSERT INTO messages_"+self.channel+"\
                              (inprogress, submit_time, data)\
                              VALUES (false, now(), %s)", [data])
        self._cursor.execute("NOTIFY messages_"+self.channel+";")
        self.conn.commit()

    def post_all(self, data):
        self._cursor.executemany("INSERT INTO messages_"+self.channel+"\
                              (inprogress, submit_time, data)\
                              VALUES (false, now(), %s)", [(d,) for d in data])
        self._cursor.execute("NOTIFY messages_"+self.channel+";")
        self.conn.commit()

    def _clear_notifies(self):
        del self.conn.notifies[:]

    def _unlisten(self):
        self._cursor.execute("UNLISTEN messages_"+self.channel+";")
        self.conn.commit()
        self.conn.poll()
        self._clear_notifies()

    def get_sync(self):
        # Fastpath: try to get something immediately.
        m = self.get_async()
        if m: return m

        c = self._cursor
        c.execute("LISTEN messages_"+self.channel+";")
        self.conn.commit()
        while True:
            if len(self.conn.notifies) == 0:
                select.select([self.conn],[],[], 30) # sleep for at most 30sec
            self.conn.poll()
            self._clear_notifies()
            m = self.get_async()
            if m:
                self._unlisten() # don't listen while processing job.
                return m

    def get_async(self):
        self._cursor.execute("SELECT id, data FROM messages_"+self.channel+
                  " WHERE inprogress is false ORDER BY id LIMIT 1 FOR UPDATE")
        res = self._cursor.fetchone()
        if res is not None:
            (rowid, data) = res
            self._cursor.execute("UPDATE messages_"+self.channel+
                      " SET (inprogress, host, pid)=(true,%s,%s) WHERE id = %s",
                      [self._host, self._pid, rowid])
            self.conn.commit()
            return Message(self, data, rowid)
        else:
            self.conn.commit()
            return None
    def _ack_message(self, rowid):
        self._cursor.execute("DELETE FROM messages_"+self.channel+
                            " WHERE id = %s;", [rowid])
        self.conn.commit()
    def _unack_message(self, rowid):
        self._cursor.execute("UPDATE messages_"+self.channel+
                            " SET inprogress=false WHERE id = %s;", [rowid])
        self.conn.commit()
