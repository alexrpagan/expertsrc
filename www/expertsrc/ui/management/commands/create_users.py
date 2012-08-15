# Script to generate a random question workload from empty
# database. Run 'python manage.py cleanup' to revert database to its
# prior state. Answering ability is normally distributed across users,
# with mean=70% correct. Every question is reviewed, and every review
# is correct.  NB: currently question quotas are ignored. this should
# be addressed in future versions.

from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from ui.models import *
from ui.dbaccess import *
from django.db import connection, transaction 

import random

NUMBER_OF_QUESTIONS=100
NUMBER_OF_ANSWERERS=20
AVERAGE_ACCURACY=.8
STD_DEV_OF_ACCURACY=.05
AVERAGE_PERCENT_TRUE=.6

def generate_names(limit=NUMBER_OF_ANSWERERS):
    return ['ans'+str(x) for x in range(1, limit+1)]

def get_expected_correct_rate(mu=AVERAGE_ACCURACY, sigma=STD_DEV_OF_ACCURACY):
    while True:
        confidence_guess = random.gauss(mu=mu, sigma=sigma)
        if 0 <= confidence_guess <= 1:
            break
    return confidence_guess

class Command(NoArgsCommand):
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        print 'creating data-tamer domain...'
        domain = Domain()
        domain.short_name = 'data-tamer'
        domain.long_name = 'Data Tamer Questions'
        domain.description = 'lorem ipsum'
        domain.save()

        print 'creating levels...'
        for x in range(1, 4):
            level = Level(domain=domain, 
                          level_number=x, 
                          confidence_upper_bound=(.6 + x*.1))
            level.save()
        level = Level(domain=domain,
                      level_number=4,
                      confidence_upper_bound=1)
        level.save()

        print 'creating fake asker...'
        asker = User.objects.create_user('ask', '', 'test')
        asker.save()
        profile = UserProfile(user=asker,
                              user_class='ASK',
                              bank_balance=1000)
        profile.save()

        
        answerers = []
        print 'creating fake answerers...'
        expected_percent_correct = {}
        for name in generate_names():
            u = User.objects.create_user(name, '', 'test')
            answerers.append(u)
            expected_percent_correct[u] = get_expected_correct_rate()
            
        print 'creating wolfgang...'
        wg = User.objects.create_user('wolfgang', '', 'test')
        answerers.append(wg)
        expected_percent_correct[wg] = 1
        
        for user in answerers:
            user.save()
            profile = UserProfile(user=user, 
                                  user_class='ANS',
                                  bank_balance=0)
            profile.save()
            
            e = Expertise(user=profile, domain=domain, question_quota=50)
            e.save()

        print 'creating a phony data tamer application'
        app = Application()
        app.name = 'data-tamer'
        app.db_alias = settings.TAMER_DB
        app.ui_url = settings.TAMER_URL
        app.save()

        print 'creating training question type'
        train = QuestionType()
        train.long_name = 'Training questions'
        train.short_name = 'training'
        train.app = app
        train.question_class = ContentType.objects.get(app_label='ui', model='nrtrainingquestion')
        train.answer_class = ContentType.objects.get(app_label='ui', model='nrtraininganswer')
        train.review_class = ContentType.objects.get(app_label='ui', model='nrtrainingreview')
        train.save()

        print 'creating automated schema map question type'
        schemamap = QuestionType()
        schemamap.long_name = 'Schema mapping questions'
        schemamap.short_name = 'schemamap'
        schemamap.app = app
        schemamap.question_class = ContentType.objects.get(app_label='ui', model='schemamapquestion')
        schemamap.answer_class = ContentType.objects.get(app_label='ui', model='schemamapanswer')
        schemamap.review_class = ContentType.objects.get(app_label='ui', model='schemamapreview')
        schemamap.save()
        
        print 'creating some phony questions...'
        for x in range(0, NUMBER_OF_QUESTIONS):
            question = NRTrainingQuestion(asker=asker,
                                          domain=domain,
                                          question_type=train)
            question.save()

            choice_set = []
            number_of_choices = random.randint(3, 6)
            correct_choice_idxs = [x for x in range(0, number_of_choices)]
            
            # select the choices that are "true" with frequency specified above
            for x in range(0, number_of_choices):
                rand = random.random()
                if rand > AVERAGE_PERCENT_TRUE:
                    correct_choice_idxs.remove(x)
            
            # make the choice rows
            for x in range(0, number_of_choices):
                choice = NRTrainingChoice(question=question)
                choice.save()
                choice_set.append(choice)
                
            # need to make a copy as we will be randomly assigning answerers to questions
            # and removing them as we go to ensure that the same user isn't assigned
            # twice to the same question.
            copy_of_answerers = list(answerers)

            # modify the range of random.randint to get differently-sized allocations.
            for x in range(0, random.randint(3,6)):
                answerer = random.choice(copy_of_answerers)
                copy_of_answerers = filter(lambda a: a.id != answerer.id, answerers)
                assgn = Assignment(answerer=answerer, question=question, completed=False)
                assgn.save()

                # now have the user supply answers to questions
                for x in range(0, number_of_choices):
                    choice = choice_set[x]
                    
                    # flip weighted coin to determine correctness
                    is_correct=False
                    rand = random.random()
                    if rand <= expected_percent_correct[answerer]:
                        is_correct=True

                    is_match = False
                    if is_correct and x in correct_choice_idxs:
                        is_match = True

                    answer = NRTrainingAnswer(answerer=answerer,
                                              question=question,
                                              confidence=1, 
                                              authority=1)
                    answer.save()

                    assgn.completed = True
                    assgn.save()

                    # here, every "answer" entry is reviewed immediately after it is
                    # submitted. as the answers are submitted in bulk, this will never
                    # happen in a real deployment
                    review = NRTrainingReview(reviewer=asker,
                                              answer=answer,
                                              is_correct=is_correct,
                                              confidence=1,
                                              authority=1)
                    review.save()


        print 'sending training questions three weeks into the past...'
        cur = connection.cursor()
        cur.execute('select * from time_warp_training_questions()')
        cur.connection.commit()
 
        # print 'setting level prices...'
        # update_prices()

        print 'done!' 

        
