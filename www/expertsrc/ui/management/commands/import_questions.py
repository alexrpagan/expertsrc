from django.core.management.base import NoArgsCommand
from django.db import transaction
from ui.models import *
from ui.dbaccess import *
from protocol import expertsrc_pb2
from protocol.batchqueue import BatchQueue

import redis
import django

class Command(NoArgsCommand):

    @transaction.commit_on_success
    def create_schemamap_batch(self, batch_obj):
        batch_rec = Batch()
        batch_rec.owner = User.objects.get(username=batch_obj.asker_name)
        batch_rec.question_type = QuestionType.objects.get(short_name='schemamap')
        batch_rec.source_name = batch_obj.source_name
        batch_rec.save()
        for question in batch_obj.question:
            smq = SchemaMapQuestion()
            smq.batch = batch_rec
            smq.asker = batch_rec.owner 
            smq.domain = Domain.objects.get(short_name='data-tamer')
            smq.question_type = QuestionType.objects.get(short_name='schemamap')
            smq.local_field_id = question.local_field_id
            smq.local_field_name = question.local_field_name
            smq.save()
            for choice in question.choice:
                smc = SchemaMapChoice()
                smc.question = smq
                smc.global_attribute_id = choice.global_attribute_id
                smc.global_attribute_name = choice.global_attribute_name
                smc.confidence_score = choice.confidence_score
                smc.save()
        #self.allocate_schemamap_batch(batch_rec)

    @transaction.commit_on_success
    def allocate_schemamap_batch(self, batch):
        for q in SchemaMapQuestion.objects.filter(batch=batch):
            allocs = get_allocations(q)
            allocation = random.choice(allocs)
            for member in allocation.members:
                assn = Assignment()
                assn.answerer = User.objects.get(pk=member)
                assn.question = q
                assn.completed = False
                assn.save()
        print 'Completed: %s' % batch.id

    def handle_noargs(self, **options):
        print 'importing schema mapping questions from data tamer'
        batch_obj = expertsrc_pb2.QuestionBatch()
        batch = BatchQueue('question', batch_obj)
        while True:
            try:
                while True:
                    batch.dequeue()
                    print 'dequeue question batch'
                    batch_obj = batch.getbatchobj()
                    if batch_obj.type == expertsrc_pb2.QuestionBatch.SCHEMAMAP:
                        self.create_schemamap_batch(batch_obj)
            except redis.exceptions.ConnectionError:
                print 'trying to reconnect . . . '
                batch.reconnect()
            except KeyboardInterrupt:
                print 'caught keyboard interrupt, bailing out . . .'
                break
            except django.db.utils.IntegrityError:
                print 'tried to create a duplicate question for a field. ignoring'
            except Exception, e:
                raise e
