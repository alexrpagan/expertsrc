from django.db import models, connections, transaction
from django.db.backends.signals import connection_created
from django.forms import ModelForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings

from ui.dbaccess import *
from ui.utils import *

import logging
import datetime
import sys
import traceback

logger = logging.getLogger(__name__)

####
#### signal recievers
####


def set_search_path(sender, **kwargs):
    cursor = connections["default"].cursor()
    cursor.execute("SET search_path TO public")

connection_created.connect(set_search_path)

# maximum length given to all character string fields.
MAX_CHAR_LENGTH = 32


class InsufficientFundsException(Exception):
    pass


class UserFunctions:

    def is_asker(self):
        return self.get_profile().user_class == 'ASK'

    def is_answerer(self):
        return self.get_profile().user_class == 'ANS'

    def has_logged_in(self):
        return self.get_profile().has_logged_in

    def set_login(self):
        profile = self.get_profile()
        profile.has_logged_in = True
        profile.login_date = datetime.datetime.now()
        profile.save()

    def has_consented(self):
        return self.get_profile().has_consented

    def set_consent(self, answer):
        profile = self.get_profile()
        if answer:
            profile.has_consented = answer
        profile.consent_date = datetime.datetime.now()
        profile.save()

    def has_completed_training(self):
        return self.get_profile().has_completed_training

    def set_training(self):
        profile = self.get_profile()
        profile.has_completed_training = True
        profile.training_completion_date = datetime.datetime.now()
        profile.save()

    def get_all_jobs(self, domain):
        questions = BaseQuestion.objects.filter(domain=domain)
        return Assignment.objects.filter(answerer=self,
                                         question__in=questions).order_by('create_time')

    def get_jobs(self, domain):
        questions = BaseQuestion.objects.filter(domain=domain)
        return Assignment.objects.filter(answerer=self,
                                         completed=False,
                                         question__in=questions).order_by('create_time')

    def get_review_jobs(self):
        jobs = ReviewAssignment.objects.filter(reviewer=self, completed=False).order_by('create_time')[:10]
        return jobs

    @transaction.commit_on_success
    def get_paid(self, question):
        """ this assumes that the questions are batched and that the user is an answerer"""
        profile = self.get_profile()
        batch = question.batch
        assgn = Assignment.objects.get(answerer=self, completed=True, question=question)
        funds = batch.budget
        price = assgn.agreed_price
        if funds < price:
            msg = "There is not enough money allocated to pay user %s" % self.username
            raise InsufficientFundsException(msg)
        else:
            batch.budget -= price
            batch.save()
            profile.bank_balance += price
            profile.save()

    @transaction.commit_on_success
    def pay_out(self, batch, price):
        "This also assumes that questions are batched and that the user is an asker"
        profile = self.get_profile()
        if profile.bank_balance < price:
            msg = "You do not have enough money to pay for these allocations. Your balance is: %s"
            raise InsufficientFundsException(msg % profile.bank_balance)
        else:
            profile.bank_balance -= price
            profile.save()
            batch.budget += price
            batch.save()

User.__bases__ += (UserFunctions,)


class Feedback(models.Model):
    SENTIMENTS = (
        (1, 'Positive'),
        (0, 'Mixed'),
        (-1, 'Negative'),
    )
    user = models.ForeignKey(User)
    sentiment = models.IntegerField(choices=SENTIMENTS)
    improvements = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        exclude = ('user',)


class Domain(models.Model):
    # no spaces here.
    short_name = models.CharField(max_length=MAX_CHAR_LENGTH)
    long_name = models.CharField(max_length=MAX_CHAR_LENGTH)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.short_name


class UserProfile(models.Model):
    USER_CLASS_CHOICES = (
        ('ASK', 'Asker'),
        ('ANS', 'Answerer')
    )
    user = models.OneToOneField(User)
    user_class = models.CharField(max_length=3, choices=USER_CLASS_CHOICES)
    bank_balance = models.FloatField(default=0)
    domains = models.ManyToManyField(Domain, through='Expertise')
    has_logged_in = models.BooleanField(default=False)
    login_date = models.DateTimeField(null=True, blank=True)
    has_completed_training = models.BooleanField(default=False)
    training_completion_date = models.DateTimeField(null=True, blank=True)
    has_consented = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    has_been_assigned = models.BooleanField(default=False)


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('domains', 'user', 'bank_balance',)


class TempAccuracy(models.Model):
    user = models.ForeignKey(User)
    accuracy = models.FloatField(default=.5)


class Level(models.Model):
    domain = models.ForeignKey(Domain)
    level_number = models.IntegerField()
    confidence_upper_bound = models.FloatField()
    price = models.FloatField(default=0)


# relation designating areas in which the user ostensibly has
# expertise.  set by the user.
class Expertise(models.Model):
    user = models.ForeignKey(UserProfile)
    domain = models.ForeignKey(Domain)
    question_quota = models.IntegerField(default=0)


class ExpertiseForm(ModelForm):
    class Meta:
        model = Expertise
        exclude = ('user',)

####
#### Models for registering applications with expertsrc
####

from django.core.exceptions import ValidationError


def validate_db_alias(value):
    from django.db import connections
    if value not in connections:
        raise ValidationError(u'Database %s has not been configured.' % value)


class Application(models.Model):
    name = models.CharField(max_length=MAX_CHAR_LENGTH)
    db_alias = models.CharField(max_length=128, null=True, blank=True, validators=[validate_db_alias])
    ui_url = models.URLField(null=True, blank=True)
    batch_budget = models.FloatField(null=True, blank=True)
    avg_confidence = models.FloatField(null=True, blank=True)
    batch_size = models.PositiveIntegerField(default=0)

    def get_external_db_conn(self):
        if self.db_alias is not None:
            return connections[self.db_alias]

###
### Base classes for question types
###


class QuestionType(models.Model):
    long_name = models.CharField(max_length=MAX_CHAR_LENGTH)
    short_name = models.CharField(max_length=MAX_CHAR_LENGTH)
    app = models.ForeignKey(Application)
    price = models.FloatField(default=0)
    question_class = models.ForeignKey(ContentType, related_name="+")
    answer_class = models.ForeignKey(ContentType, related_name="+")
    review_class = models.ForeignKey(ContentType, related_name="+")


# TODO: change name to question batch
class Batch(models.Model):
    owner = models.ForeignKey(User)
    source_name = models.CharField(max_length=128, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_allocated = models.BooleanField(default=False)
    question_type = models.ForeignKey(QuestionType)
    budget = models.FloatField(default=0)


class BaseQuestion(models.Model):
    asker = models.ForeignKey(User)
    domain = models.ForeignKey(Domain)
    submit_time = models.DateTimeField(auto_now_add=True)
    question_type = models.ForeignKey(QuestionType)
    batch = models.ForeignKey(Batch, blank=True, null=True)

    @staticmethod
    def get_gui_url(user_id, jobs):
        """ Build a url for accessing the answering interface of this type of question."""
        raise NotImplementedError

    @staticmethod
    def get_confidence_score(allocation, db_data):
        """
        Compute the confidence for an allocation.

        Allows the implementer to pass along needed data.

        TODO: Create an alternate implementation that allows data to be
        fetched from within the method (pass along plpy object?)
        """
        pass


class BaseChoice(models.Model):
    question = models.ForeignKey(BaseQuestion)


class BaseAnswer(models.Model):
    question = models.ForeignKey(BaseQuestion)
    answerer = models.ForeignKey(User)
    start_time = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField()
    authority = models.FloatField()


class BaseReview(models.Model):
    reviewer = models.ForeignKey(User)
    answer = models.ForeignKey(BaseAnswer)
    is_correct = models.BooleanField()
    feedback = models.TextField(null=True, blank=True)
    confidence = models.FloatField()
    authority = models.FloatField()


class BatchSupport:
    @staticmethod
    def import_batch(batch_obj):
        """
        Create DB records for one batch of questions imported from queue.
        """
        raise NotImplementedError


class Assignment(models.Model):
    answerer = models.ForeignKey(User)
    completed = models.BooleanField()
    complete_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(BaseQuestion)
    agreed_price = models.FloatField(default=0)


class ReviewAssignment(models.Model):
    reviewer = models.ForeignKey(User)
    completed = models.BooleanField()
    complete_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    answer = models.ForeignKey(BaseAnswer)
    agreed_price = models.FloatField(default=0)


# class ERQuestion(BaseQuestion, BatchSupport):
#     entity1 = models.IntegerField(default=0)
#     entity2 = models.IntegerField(default=0)
#     source_id = models.IntegerField(default=0)
#     cluster_id = models.IntegerField(default=0)

#     def __unicode__(self):
#         return '%s -> %s' % (self.entity1, self.entity2)

#     @staticmethod
#     @transaction.commit_on_success
#     def import_batch(batch_obj):
#         batch_rec = Batch()
#         batch_rec.owner = User.objects.get(username=batch_obj.asker_name)
#         batch_rec.question_type = QuestionType.objects.get(short_name='nr')
#         batch_rec.source_name = batch_obj.source_name
#         batch_rec.save()
#         for question in batch_obj.question:
#             erq = Question()
#             erq.batch = batch_rec
#             erq.asker = batch_rec.owner
#             erq.domain = Domain.objects.get(short_name=question.domain_name)
#             erq.question_type = QuestionType.objects.get(short_name='nr')
#             erq.entity1 = question.entity1
#             erq.entity2 = question.entity2
#             erq.source_id = question.source_id
#             erq.save()


# class ERAnswer(BaseAnswer, BatchSupport):
#     is_dup = models.BooleanField()
#     fid_answer_cnt = {}
#     reviewer = None
#     for answer in batch_obj.answer:
#         answerer = User.objects.get(pk=answer.answerer_id)
#         era = ERAnswer()
#         question = sma.question = ERQuestion.objects.get(entity1=answer.entity1, entity2=answer.entity2)
#         sma.answerer = answerer
#         sma.confidence = answer.confidence
#         sma.authority = answer.authority
#         sma.global_attribute_id = answer.global_attribute_id
#         fid_answer_cnt.setdefault(answer.local_field_id,
#                                   SchemaMapAnswer.objects.filter(answerer=answerer,
#                                                                  local_field_id=answer.local_field_id).count())
#         sma.local_field_id = answer.local_field_id
#         sma.is_match = answer.is_match
#         sma.save()
#         assn = Assignment.objects.get(answerer=answerer, question=sma.question)
#         assn.completed = True
#         assn.save()
#         # only pay for one answer per local_field_id
#         if fid_answer_cnt[answer.local_field_id] == 0:
#             answerer.get_paid(question)
#             fid_answer_cnt[answer.local_field_id] += 1

class SchemaMapQuestion(BaseQuestion, BatchSupport):
    local_field_id = models.PositiveIntegerField(unique=True)
    local_field_name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.local_field_name

    @staticmethod
    @transaction.commit_on_success
    def import_batch(batch_obj):
        batch_rec = Batch()
        batch_rec.owner = User.objects.get(username=batch_obj.asker_name)
        batch_rec.question_type = QuestionType.objects.get(short_name='schemamap')
        batch_rec.source_name = batch_obj.source_name
        batch_rec.save()
        for question in batch_obj.question:
            smq = SchemaMapQuestion()
            smq.batch = batch_rec
            smq.asker = batch_rec.owner
            smq.domain = Domain.objects.get(short_name=question.domain_name)
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

    @staticmethod
    def get_gui_url(user_id, jobs):
        """
        Get a url for this and all other questions currently in the question
        queue. Later, should limit this to a reasonable number of questions.

        This assumes that the jobs list is non-empty
        """
        assert len(jobs) > 0
        domain_id = jobs[0].question.domain.id
        fields = ','.join([str(job.question.schemamapquestion.local_field_id) for job in jobs])
        redirect_base = '%s/doit/%s/fields/map?answerer_id=%s&fields=%s&domain_id=%s'
        redirect_url = redirect_base % (settings.TAMER_URL, settings.TAMER_DB, user_id, fields, domain_id)
        return redirect_url

    @staticmethod
    def get_confidence_score(db_data):
        pass


class SchemaMapChoice(BaseChoice):
    global_attribute_id = models.PositiveIntegerField()
    global_attribute_name = models.CharField(max_length=128)
    confidence_score = models.FloatField(default=0)


class SchemaMapAnswer(BaseAnswer, BatchSupport):
    local_field_id = models.PositiveIntegerField(default=0)
    global_attribute_id = models.PositiveIntegerField(default=0)
    is_match = models.BooleanField()

    def register_for_review(self, reviewer=None):
        """ Give the answer to a reviewer to be validated. """
        if reviewer is None:
            raise Exception("no reviewer")
        else:
            rev_assgn = ReviewAssignment()
            rev_assgn.reviewer = reviewer
            rev_assgn.completed = False
            rev_assgn.answer = self
            rev_assgn.agreed_price = 0
            rev_assgn.save()

    @staticmethod
    @transaction.commit_on_success
    def import_batch(batch_obj):
        """
        Note: this currently always allocates the same reviewer to every question.
        Change this.
        """
        fid_answer_cnt = {}
        reviewer = None
        for answer in batch_obj.answer:
            answerer = User.objects.get(pk=answer.answerer_id)
            sma = SchemaMapAnswer()
            question = sma.question = SchemaMapQuestion.objects.get(local_field_id=answer.local_field_id)
            sma.answerer = answerer
            sma.confidence = answer.confidence
            sma.authority = answer.authority
            sma.global_attribute_id = answer.global_attribute_id
            fid_answer_cnt.setdefault(answer.local_field_id,
                                      SchemaMapAnswer.objects.filter(answerer=answerer,
                                                                     local_field_id=answer.local_field_id).count())
            sma.local_field_id = answer.local_field_id
            sma.is_match = answer.is_match
            sma.save()
            assn = Assignment.objects.get(answerer=answerer, question=sma.question)
            assn.completed = True
            assn.save()
            # only pay for one answer per local_field_id
            if fid_answer_cnt[answer.local_field_id] == 0:
                answerer.get_paid(question)
                fid_answer_cnt[answer.local_field_id] += 1


class SchemaMapReview(BaseReview, BatchSupport):
    @staticmethod
    @transaction.commit_on_success
    def import_batch(batch_obj):
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


class NRTrainingQuestion(BaseQuestion):
    pass


class NRTrainingChoice(BaseChoice):
    pass


class NRTrainingAnswer(BaseAnswer):
    pass


class NRTrainingReview(BaseReview):
    pass
