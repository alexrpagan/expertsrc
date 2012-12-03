import redis

class BatchQueue:
    """ 
    Naive Redis-based message queue.
    """
    batch_obj = None
    queue_name = None
    conn = None

    class DisconnectedException(BaseException):
        """
        It has been observed that sometimes the redis connection will
        be dropped while blocking on a dequeue operation. This exception
        is thrown in place of a redis connection error.
        """
        pass
    
    def __init__(self, queue_name, batch_obj):
        """
        Each batch queue wants the name of the queue (e.g. questions)
        and also a batch object.

        NOTE: Type of the batch object must match the type of objects in the
        queue (e.g. QuestionBatch) or else deserialization will fail.
        """
        self.conn = redis.Redis(port=6379)
        self.batch_obj = batch_obj
        self.queue_name = queue_name

    def enqueue(self):
        """
        Attempts to serialize the current contents of the batch object,
        then insert that into the queue.
        """
        buf = self.batch_obj.SerializeToString()
        self.conn.rpush(self.queue_name, buf)

    def dequeue(self):
        """ 
        Attempts to grab and deserialize the most recent batch from queue
        into the batch object.
        Blocks if queue is empty.
        """
        try:
            buf = self.conn.blpop(self.queue_name)
        except redis.exceptions.ConnectionError:
            raise DisconnectedException()
        self.batch_obj.ParseFromString(buf[1])

    def getbatchobj(self):
        return self.batch_obj
    
    def reconnect(self):
        self.conn = None
        self.conn = redis.Redis()


