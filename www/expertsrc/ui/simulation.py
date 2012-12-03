from ui.models import *
from django.contrib.auth.models import User
from django.db import connection, transaction
import ui.dbaccess as db
import ui.pricing.staticprice as sp
import ui.pricing.dynprice as dp
import ui.workerstats.allocations as allocs
import ui.workerstats.confidence as conf
import pickle
import random
import math


CONFIG = {
    'number_of_batches': 100,
   	'worker_ability_mean': 1.44,
   	'worker_ability_stddev': .59,
    'worker_pop_size': 100,
	'batch_size_mean': 10,
	'batch_size_stddev': 2,
	'reprice_frequency': 3, # in batches
    'confidence_req': .90,
    'confidence_req_mean': 2.5,
    'confidence_req_stddev': .0001,
    'max_price_mean': 300,
    'max_price_stddev': 50,
    'min_price_prob':1,
    'asker_budget': 10000000,
    'max_allocation_size': 12,
    'levels': {1: .7, 2: .8, 3: .9},
	'quotas': {1: 50, 2: 30, 3: 10},
}


USERS = {
    # store "true ability" here.
}


ANS_CODE = 'ANS'
ASK_CODE = 'ASK'

AVAILS = []
PRICES = []
ALLOCATIONS = []


def dump_data(filename):
    abilities = [USERS[x] for x in USERS.keys()]
    with open(filename, 'w') as f:
        pickle.dump((CONFIG, abilities, ALLOCATIONS, AVAILS, PRICES), f)


def setup_market():
    global DOMAIN
    global APP
    global TYPE
    global ASKER
    print 'creating domain record'
    DOMAIN = create_domain()
    print 'creating user level records'
    create_levels()
    print 'creating asker user'
    ASKER = create_asker()
    print 'creating answerers'
    create_answerers(DOMAIN)
    print 'creating application record'
    APP = create_application()
    print 'create question type record'
    TYPE = create_question_type(APP)
    print 'creating and pricing allocations'
    create_allocations()


def run_experiment():
    bn = CONFIG['number_of_batches']
    rr = CONFIG['reprice_frequency'] 
    for i in range(bn):
        print 'batch #%d' % (i + 1)
        reprice = (i % rr == 0)
        res = do_batch(reprice) 
        if not res:
            print 'something bad happened!'
            return
 

def create_domain():
    domain = Domain()
    domain.short_name = 'data-tamer-synth'
    domain.long_name = 'Fake Domain'
    domain.description = 'a fake domain.'
    domain.save()
    return domain


def create_levels():
    levels = CONFIG['levels']
    assert DOMAIN
    for key in levels:
        level = Level(domain=DOMAIN, 
                      level_number=key, 
                      confidence_upper_bound=levels[key])
        level.save()


def create_asker():
    asker_budget = CONFIG['asker_budget'] 
    asker = User.objects.create_user('ask-synth', '', 'test')
    asker.save()
    profile = UserProfile(user=asker,
                          user_class=ASK_CODE,
                          bank_balance=asker_budget)
    profile.save()
    return asker


def create_answerers(domain):
    mu = CONFIG['worker_ability_mean']
    sigma = CONFIG['worker_ability_stddev']
    quotas = CONFIG['quotas']
    levels = CONFIG['levels']
    ability = 0.
    for name in generate_names(CONFIG['worker_pop_size']):
        u = User.objects.create_user(name, '', 'test')
        u.save()
        USERS[u] = ability = prob_correct(random.gauss(mu, sigma))
        p = UserProfile(user=u,
                        user_class=ANS_CODE,
                        bank_balance=0)
        p.save()
        temp_acc = TempAccuracy(user=u, accuracy=ability)
        temp_acc.save()
        #TODO: level-based question quotas
        userlevel = 1
        for l in sorted(levels.keys()):
            if ability >= levels[l]:
                userlevel = l
            else:
                break
        e = Expertise(user=p, domain=domain, question_quota=quotas[userlevel])
        e.save()

    
def create_application():
    app = Application()
    app.name = 'data-tamer-synth'
    app.db_alias = settings.TAMER_DB
    app.ui_url = settings.TAMER_URL
    app.save()
    return app 


def create_question_type(app):
    train = QuestionType()
    train.long_name = 'Training questions'
    train.short_name = 'training-synth'
    train.app = app
    train.question_class = ContentType.objects.get(app_label='ui', model='nrtrainingquestion')
    train.answer_class = ContentType.objects.get(app_label='ui', model='nrtraininganswer')
    train.review_class = ContentType.objects.get(app_label='ui', model='nrtrainingreview')
    train.save()
    return train
   

def create_allocations():
    max_size = CONFIG['max_allocation_size']
    allocs.generate_and_insert(max_size)


def get_prices(domain):
    prices = {}
    for level in Level.objects.filter(domain_id=domain):
         prices[level.level_number] = level.price
    return prices


def take_system_snapshot():
    AVAILS.append(db.get_availability_histo(DOMAIN.id))
    PRICES.append(get_prices(DOMAIN.id))


def do_batch(reprice=False):
    batch_mu       = CONFIG['batch_size_mean']
    batch_sigma    = CONFIG['batch_size_stddev']
    min_price_prob = CONFIG['min_price_prob']
    conf_mu        = CONFIG['confidence_req_mean']
    conf_sigma     = CONFIG['confidence_req_stddev']
    price_mu       = CONFIG['max_price_mean']
    price_sigma    = CONFIG['max_price_stddev']
#    if random.random() < min_price_prob:
#        method = 'min_price'
#        crit = sigmoid(random.gauss(conf_mu, conf_sigma))
#    else:
#        method = 'max_conf'
#        crit = random.gauss(price_mu, price_sigma)
    batch_size = int(max([1, math.ceil(random.gauss(batch_mu, batch_sigma))]))
    # get answerers
    assgns = db.create_assignments(DOMAIN.id, .9, batch_size, 'min_price')
    if not assgns:
        print "failing over to max_conf"
        assgns = db.create_assignments(DOMAIN.id, 10000, batch_size, 'max_conf')
        if not assgns:
            return 
    # create questions
    questions = {}
    for x in range(batch_size):
        q = NRTrainingQuestion(asker=ASKER, 
                               domain=DOMAIN,
                               question_type=TYPE)
        q.save()
        true = NRTrainingChoice(question=q)
        true.save()
        false = NRTrainingChoice(question=q)
        false.save()
        assgn = assgns[x]
        ALLOCATIONS.append(assgn.get_dict())
        for u in assgn.members:
            keymatch = lambda z: z.id == u
            user_rec = filter(keymatch, USERS.keys())[0]
            user_acc = USERS[user_rec]
            a = Assignment(answerer=user_rec, question=q, completed=True)
            a.save()
            chosen = false
            if random.random() <= user_acc:
                chosen = true
            answer = NRTrainingAnswer(answerer=user_rec,
                                      question=q,
                                      confidence=1.,
                                      authority=1.)
            answer.save()
            review = NRTrainingReview(reviewer=ASKER,
                                      answer=answer,
                                      is_correct=(chosen == true),
                                      confidence=1.,
                                      authority=1.)
            review.save()
    if reprice:
        dp.update_prices()
        allocs.update_prices(DOMAIN.id)
    db.log_market_stats(DOMAIN.id)
    take_system_snapshot()    
    return True


def cleanup():
    User.objects.filter(username__startswith='ask-synth').delete()
    User.objects.filter(username__startswith='ans-synth').delete()
    domain = Domain.objects.filter(short_name='data-tamer-synth')
    did = domain[0].id
    domain.delete()
    Application.objects.filter(name='data-tamer-synth').delete()
    print 'deleting market history'
    cur = connection.cursor()
    cur.execute('delete from market_snap where domain_id = %s;', (did,))
    cur.connection.commit()



def prob_correct(ability, difficulty=1):
    return sigmoid(ability ** (1. / difficulty))


def sigmoid(x):
    return 1 / (1 + math.exp(-x)) 


def generate_names(number):
    return ['ans-synth%s' % x for x in range(1, number+1)]


