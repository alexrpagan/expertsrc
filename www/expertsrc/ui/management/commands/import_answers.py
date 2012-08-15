from django.core.management.base import NoArgsCommand
from django.db import transaction
from ui.dbaccess import *
from ui.models import *
from protocol import expertsrc_pb2
from protocol.batchqueue import BatchQueue
import redis

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def create_schemamap_batch(self, batch_obj):
        """
        Note: this currently always allocates the same reviewer to every question.
        Change this.
        """
        reviewer = None
        for answer in batch_obj.answer:
            answerer = User.objects.get(pk=answer.answerer_id)
            sma = SchemaMapAnswer()
            question = sma.question = SchemaMapQuestion.objects.get(local_field_id=answer.local_field_id)
            if not reviewer:
                reviewer_dict = select_reviewer(question.domain)
                reviewer = User.objects.get(pk=reviewer_dict['user_id'])
            sma.answerer = answerer
            sma.confidence = answer.confidence
            sma.authority = answer.authority
            sma.global_attribute_id = answer.global_attribute_id
            sma.local_field_id = answer.local_field_id
            sma.is_match = answer.is_match
            sma.save()
            sma.register_for_review(reviewer=reviewer)
            assn = Assignment.objects.get(answerer=answerer, question=sma.question)
            assn.completed = True
            assn.save()
            answerer.get_paid(question)

    def handle_noargs(self, **options):
        print 'importing schema mapping answers from data tamer'
        batch_obj = expertsrc_pb2.AnswerBatch()
        batch = BatchQueue('answer', batch_obj)
        while True:
            try:
                while True:
                    batch.dequeue()
                    print 'dequeue answer batch'
                    batch_obj = batch.getbatchobj()
                    if batch_obj.type == expertsrc_pb2.AnswerBatch.SCHEMAMAP:
                        self.create_schemamap_batch(batch_obj)
                    print 'saved answers'
            except redis.exceptions.ConnectionError:
                print 'trying to reconnect . . . '
                batch.reconnect()
            except KeyboardInterrupt:
                print 'caught keyboard interrupt, bailing out . . .'
                break 
            except Exception, e:
                raise e

