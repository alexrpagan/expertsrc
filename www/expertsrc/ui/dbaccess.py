from collections import Counter
from django.db import connection, transaction
import ui.utils as utils
import ui.pricing.staticprice as sp
import ui.pricing.dynprice as dp
import ui.workerstats.allocations as alloc 
import pulp
import decimal

@transaction.commit_on_success
def get_answerer_domain_overview(user):
    cursor = connection.cursor()
    cmd = """ SELECT o.*, o.num_answered + o.num_pending as total_answered
              FROM answerer_overview as o WHERE user_id = %s """
    cursor.execute(cmd, [user.id])
    return utils.dictfetchall(cursor)


@transaction.commit_on_success
def get_overview_record(user, domain):
    cursor = connection.cursor()
    cmd = """ SELECT user_level, price FROM answerer_overview
              WHERE user_id = %s and domain_id = %s """
    cursor.execute(cmd, [user.id, domain.id])
    res = utils.dictfetchall(cursor)
    return res[0]


@transaction.commit_on_success
def get_global_user_overview():
    cursor = connection.cursor()
    cmd = """ SELECT username, short_name, question_quota,
                     accuracy, user_level, num_pending
              FROM answerer_overview as o
              ORDER BY o.accuracy DESC, o.short_name """
    cursor.execute(cmd)
    res = utils.dictfetchall(cursor)
    return res


@transaction.commit_on_success
# TODO: Replace this with a generic view
def get_batch_overview(batch_id):
    cursor = connection.cursor()
    cmd = """ SELECT local_field_name, number_allocated,
                     number_completed, poisson_binomial_conf as conf
              FROM batch_overview as o
              WHERE id = %s"""
    cursor.execute(cmd, (batch_id,))
    return utils.dictfetchall(cursor)


@transaction.commit_on_success
def get_availability_histo(domain_id):
    cursor = connection.cursor()
    cmd = """ SELECT user_level as level,
              SUM(num_to_answer - num_pending) as avail
              FROM answerer_overview
              WHERE domain_id = %s
              GROUP BY user_level
              ORDER BY user_level ASC """
    cursor.execute(cmd, (domain_id,))
    histo_raw = utils.dictfetchall(cursor)
    histo = Counter()
    for row in histo_raw:
        histo[row['level']] = row['avail']
    return histo


@transaction.commit_on_success
def get_level_dist(domain):
    dist = {}
    cursor = connection.cursor()
    cmd = """ SELECT user_level, count(*)
              FROM answerer_overview
              WHERE domain_id = %s
              GROUP BY user_level; """
    cursor.execute(cmd, (domain,))
    for row in cursor.fetchall():
        dist[row[0]] = row[1]
    return dist


@transaction.commit_on_success
def get_level_count(domain):
    cursor = connection.cursor()
    cmd = """ SELECT count(*)
              FROM ui_level
              WHERE domain_id = %s"""
    cursor.execute(cmd, (domain,))
    return cursor.fetchone()[0]


@transaction.commit_on_success
def get_user_list(domain):
    cursor = connection.cursor()
    cmd = """ SELECT user_id, user_level, price,
                     num_to_answer - num_pending as avail
              FROM answerer_overview
              WHERE domain_id = %s
              ORDER BY user_level DESC, avail DESC """
    cursor.execute(cmd, (domain,))
    user_list = {}
    for row in utils.dictfetchall(cursor):
        l = user_list.setdefault(row['user_level'], [])
        l.append(row)
    return user_list


@transaction.commit_on_success
def get_candidates(domain, criterion, method, limit=100):
    cursor = connection.cursor()
    histo = get_level_dist(domain)
    avail_arry = [0] * get_level_count(domain)
    for key in sorted(histo.keys()):
        avail_arry[key - 1] = histo[key]
    if method == 'min_price':
        cmd = """ SELECT dist, conf, price
                  FROM alloc_stems as a
                  WHERE all_gte(%s, dist)
                    AND conf >= %s
                    AND domain = %s
                  ORDER BY price ASC
                  LIMIT %s; """
    elif method == 'max_conf':
        cmd = """ SELECT dist, conf, price
                  FROM alloc_stems as a
                  WHERE all_gte(%s, dist)
                    AND price <= %s
                    AND domain = %s
                  ORDER BY conf DESC
                  LIMIT %s; """
    cursor.execute(cmd, (avail_arry, criterion, domain, limit,))
    return utils.dictfetchall(cursor)


def get_user_level(user, domain):
    return get_overview_record(user, domain)['user_level']


def max_conf(domain_id, max_price, number_of_questions):
    return create_assignments(domain_id, max_price, number_of_questions, 'max_conf')


def min_price(domain_id, min_conf, number_of_questions):
    return create_assignments(domain_id, min_conf, number_of_questions, 'min_price')


def get_optimal_allocations(domain, criterion, batch_size, method):
    candidates = get_candidates(domain, criterion, method, limit=1000)
    n = len(candidates)
    ilp_vars = [pulp.LpVariable('x%s' % x, 0, batch_size, pulp.LpInteger) \
                  for x in range(n)]
    prices = [candidates[i]['price'] for i in range(n)]
    confs = [candidates[i]['conf'] for i in range(n)]
    dists = [candidates[i]['dist'] for i in range(n)]
    histo = get_availability_histo(domain)
    ilp = None
    if method == 'min_price':
        ilp = pulp.LpProblem('minprice', pulp.LpMinimize)
        ilp += pulp.lpDot(prices, ilp_vars)
        ilp += pulp.lpDot(confs, ilp_vars) >= decimal.Decimal(batch_size * criterion)
    elif method == 'max_conf':
        ilp = pulp.LpProblem('maxconf', pulp.LpMaximize)
        ilp += pulp.lpDot(confs, ilp_vars)
        ilp += pulp.lpDot(prices, ilp_vars) <= decimal.Decimal(criterion)
    ilp += pulp.lpSum(ilp_vars) == batch_size
    for level in histo:
        ilp += pulp.lpDot([dists[i][level - 1] for i in range(n)], \
                          ilp_vars) <= histo[level]
    status = ilp.solve(pulp.GLPK(msg=0))
    allocs = []
    if pulp.LpStatus[status] == 'Optimal':
        for i in range(n):
            x = ilp_vars[i]
            if pulp.value(x) > 0:
                allocs.append((pulp.value(x), candidates[i]))
    return allocs


@transaction.commit_on_success
def create_assignments(domain, criterion, batch_size, method):
    assgns = []
    allocs = get_optimal_allocations(domain, criterion, batch_size, method)
    user_list = get_user_list(domain)
    for opt in allocs:
        repeat, alloc = opt
        dist = alloc['dist']
        for i in range(repeat):
            alloc_rec = Allocation()
            alloc_rec.confidence = alloc['conf']
            alloc_rec.price = alloc['price']
            alloc_membs = set()
            for lidx in range(len(dist)):
                for j in range(dist[lidx]):
                    for user in user_list[lidx + 1]:
                        if user['avail'] > 0 and \
                           user['user_id'] not in alloc_membs:
                            user['avail'] -= 1
                            alloc_membs.add(user['user_id'])
                            break
            alloc_rec.members = list(alloc_membs)
            assgns.append(alloc_rec)
    return assgns


class Allocation:
    confidence = 0.
    price = 0.
    members = None

    def __unicode__(self):
        return self.members

    def get_dict(self):
        rep = dict()
        rep['confidence'] = float(self.confidence)
        rep['price'] = float(self.price)
        rep['members'] = list(self.members)
        return rep

