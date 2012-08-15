from django.core.management.base import NoArgsCommand
from django.db import transaction
from ui.models import *
from protocol import expertsrc_pb2
from protocol.batchqueue import BatchQueue
import redis

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def create_schemamap_batch(self, batch_obj):
        for review in batch_obj.review:
            smr = SchemaMapReview()
            reviewer = smr.reviewer = User.objects.get(pk=review.reviewer_id)
            answer = smr.answer = SchemaMapQuestion.objects.get(answer_id=review.answer_id)
            smr.confidence = review.confidence
            smr.authority = review.authority
            smr.is_correct = review.is_correct
            smr.feedback = review.feedback
            smr.save()
            assgn = ReviewAssignment.objects.get(answer=answer, reviewer=reviewer)
            assgn.completed = True
            assgn.save()
            
    def handle_noargs(self, **options):
        print 'importing schema mapping reviews from data tamer'
        batch_obj = expertsrc_pb2.ReviewBatch()
        batch = BatchQueue('review', batch_obj)
        while True:
            try:
                while True:
                    batch.dequeue()
                    print 'dequeue review batch'
                    batch_obj = batch.getbatchobj()
                    if batch_obj.type == expertsrc_pb2.ReviewBatch.SCHEMAMAP:
                        self.create_schemamap_batch(batch_obj)
                    print 'saved reviews'
            except redis.exceptions.ConnectionError:
                print 'trying to reconnect . . . '
                batch.reconnect()
            except KeyboardInterrupt:
                print 'caught keyboard interrupt, bailing out . . .'
                break 
            except Exception, e:
                raise e

