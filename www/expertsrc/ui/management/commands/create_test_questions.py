from django.core.management.base import NoArgsCommand
from ui.models import *
from protocol import expertsrc_pb2
from protocol.batchqueue import BatchQueue
import random

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        print 'importing schema mapping questions from data tamer'
        batch_obj = expertsrc_pb2.QuestionBatch()
        batch_obj.type = expertsrc_pb2.QuestionBatch.SCHEMAMAP
        batch_obj.asker_name = 'data-tamer'
        batch = BatchQueue('question', batch_obj)
        for fid in random.sample(range(100), 10):
            question = batch.getbatchobj().question.add()
            question.domain_name = 'data-tamer'
            question.local_field_id = fid
            question.local_field_name = 'field%s' % fid
            for gid in random.sample(range(100), 10):
                choice = question.choice.add()
                choice.global_attribute_id = gid
                choice.global_attribute_name = 'gfield%s' % gid
                choice.confidence_score = gid % 7
        batch.enqueue()
