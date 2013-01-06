import select
import psycopg2
import psycopg2.extensions


class BatchQueue:
    """
    Naive postgres-based message queue.
    """
    batch_obj = None
    queue_name = None
    conn = None

    def __init__(self, queue_name, batch_obj):
        """
        Each batch queue wants the name of the queue (e.g. questions)
        and also a batch object.

        NOTE: Type of the batch object must match the type of objects in the
        queue (e.g. QuestionBatch) or else deserialization will fail.
        """
        self.conn = psycopg2.connect(database='doit',
                                     user='doit',
                                     password='12345',
                                     host='localhost')
        self.ac_conn = psycopg2.connect(database='doit',
                                     user='doit',
                                     password='12345',
                                     host='localhost')
        self.ac_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.batch_obj = batch_obj
        self.queue_name = queue_name

    def enqueue(self):
        """
        Attempts to serialize the current contents of the batch object,
        then insert that into the queue.
        """
        buf = self.batch_obj.SerializeToString()
        cur = self.conn.cursor()
        cmd = ''' INSERT INTO message_queue (queue_name, message) VALUES (%s, %s)'''
        cur.execute(cmd, (self.queue_name, psycopg2.Binary(buf),))
        self.conn.commit()

    def dequeue(self):
        """
        Attempts to grab and deserialize the most recent batch from queue
        into the batch object.
        Blocks on empty queue.
        """
        new_row = False
        cmd = ''' SELECT id, message FROM message_queue
                  WHERE is_seen = 'f' AND queue_name = %s
                  ORDER BY date_created DESC
                  LIMIT 1 '''
        cur = self.conn.cursor()
        cur.execute(cmd, (self.queue_name,))
        res = cur.fetchone()
        if res is not None:
            mid, buf = res
            self.batch_obj.ParseFromString(buf)
            cmd = ''' UPDATE message_queue SET is_seen = 't' WHERE id = %s '''
            cur.execute(cmd, (mid,))
            self.conn.commit()
            return
        else:
            self.conn.commit()  # close up previous txn
            ac_curs = self.ac_conn.cursor()
            ac_curs.execute('''LISTEN message_queue;''')
            while not new_row:
                if select.select([self.ac_conn], [], [], 5) == ([], [], []):
                    pass
                else:
                    self.ac_conn.poll()
                    while self.ac_conn.notifies:
                        new_row = True
                        self.ac_conn.notifies.pop()  # clear notifications from queue
        if new_row:
            self.dequeue()  # recurse and snatch row from db

    def getbatchobj(self):
        return self.batch_obj
