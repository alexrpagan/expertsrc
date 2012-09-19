from django.core.management.base import NoArgsCommand
from ui.models import *
from ui.dbaccess import *
from protocol import expertsrc_pb2
from protocol.batchqueue import BatchQueue
from django.conf import settings
import redis
import django
import threading

class QueueWatcher(threading.Thread):
    queue_name = None
    types = None
    logger = None
    batch_obj = None
    batch_queue = None
    
    def __init__(self, queue_name, types, batch_obj):
        threading.Thread.__init__(self)
        self.queue_name = queue_name
        self.types = types
        self.batch_obj = batch_obj
        self.batch_queue = BatchQueue(queue_name, batch_obj)

    def run(self):
        print 'Starting watcher on queue: %s' % self.queue_name
        while True:
            try:
                while True:
                    self.batch_queue.dequeue()
                    print 'Dequeuing %s batch.' % self.queue_name
                    for key in self.types:
                        if self.batch_obj.type == key:
                            self.types[key].import_batch(self.batch_obj)
                            break
            except BatchQueue.DisconnectedException:
                print 'Dropped connection. Reconnecting to queue %s' % self.queue_name
                batch_queue.reconnect()
            except django.db.utils.IntegrityError:
                print 'Tried to create a dup in queue: %s. Ignoring.' % self.queue_name
            except KeyboardInterrupt:
                print 'Caught keyboard interrupt. Bailing out.'
            except Exception, e:
                print 'Cause exception in queue: %s' % self.queue_name

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        # mappings between type codes in protocol buffer and django models

        question_types = {}
        question_base = expertsrc_pb2.QuestionBatch
        question_types[question_base.SCHEMAMAP] = SchemaMapQuestion

        answer_types = {}
        answer_base = expertsrc_pb2.AnswerBatch
        answer_types[answer_base.SCHEMAMAP] = SchemaMapAnswer

        review_types = {}
        review_base = expertsrc_pb2.ReviewBatch
        review_types[review_base.SCHEMAMAP] = SchemaMapReview
        
        watcher_pool = []

        watcher_pool.append(QueueWatcher(queue_name='question',
                                         types=question_types,
                                         batch_obj=expertsrc_pb2.QuestionBatch()))
        
        watcher_pool.append(QueueWatcher(queue_name='answer',
                                         types=answer_types,
                                         batch_obj=expertsrc_pb2.AnswerBatch()))

        watcher_pool.append(QueueWatcher(queue_name='review',
                                         types=review_types,
                                         batch_obj=expertsrc_pb2.ReviewBatch()))

        for watch in watcher_pool:
            watch.start()
