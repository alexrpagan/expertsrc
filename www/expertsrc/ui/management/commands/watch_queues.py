from django.core.management.base import NoArgsCommand
from ui.models import *
from ui.dbaccess import *
from protocol import expertsrc_pb2
from protocol.batchqueue import BatchQueue
import django
import threading
import sys
import logging
import Queue

logger = logging.getLogger(__name__)

class QueueWatcher(threading.Thread):
    queue_name = None
    types = None
    logger = None
    batch_obj = None
    batch_queue = None

    def __init__(self, queue_name, types, batch_obj, error_queue):
        threading.Thread.__init__(self)
        self.queue_name = queue_name
        self.types = types
        self.batch_obj = batch_obj
        self.batch_queue = BatchQueue(queue_name, batch_obj)
        self.error_queue = error_queue

    def run(self):
        logger.info('Starting watcher on queue: %s' % self.queue_name)
        while True:
            try:
                while True:
                    self.batch_queue.dequeue()
                    logger.info('Dequeuing %s batch.' % self.queue_name)
                    for key in self.types:
                        if self.batch_obj.type == key:
                            self.types[key].import_batch(self.batch_obj)
                            break
            except BatchQueue.DisconnectedException:
                logger.warning('Dropped connection. Reconnecting to queue %s' % self.queue_name)
                batch_queue.reconnect()
            except django.db.utils.IntegrityError:
                logger.warning('Tried to create a dup in queue: %s. Ignoring.' % self.queue_name)
            except:
                logger.debug('Problem in %s queue:' % self.queue_name, exc_info=sys.exc_info())
                self.error_queue.put(sys.exc_info())
                raise

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        def new_question_watcher():
            question_types = {}
            question_base = expertsrc_pb2.QuestionBatch
            question_types[question_base.SCHEMAMAP] = SchemaMapQuestion
            return QueueWatcher(queue_name='question',
                                types=question_types,
                                batch_obj=expertsrc_pb2.QuestionBatch(),
                                error_queue=Queue.Queue())

        def new_answer_watcher():
            answer_types = {}
            answer_base = expertsrc_pb2.AnswerBatch
            answer_types[answer_base.SCHEMAMAP] = SchemaMapAnswer
            return QueueWatcher(queue_name='answer',
                                types=answer_types,
                                batch_obj=expertsrc_pb2.AnswerBatch(),
                                error_queue=Queue.Queue())

        watcher_init = [new_question_watcher, new_answer_watcher]
        watcher_pool = [x() for x in watcher_init]

        for watch in watcher_pool:
            watch.start()

        while True:
            for i in range(len(watcher_pool)):
                watch = watcher_pool[i]
                try:
                    exc = watch.error_queue.get(block=False)
                except Queue.Empty:
                    pass
                else:
                    watch.join(0.1)
                    if watch.isAlive():
                        continue
                    else:
                        logger.debug('starting new %s watcher thread' % watch.queue_name)
                        watcher_pool[i] = watcher_init[i]()
                        watcher_pool[i].start() 
                        del watch
                        logger.debug('started new watcher thread successfully.')
