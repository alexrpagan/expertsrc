from django.db import connection, transaction
from itertools import izip
from ui.utils import *
from ui.pricing import *
import random
import logging
import itertools
import math

from ui.models import *

import ui

def get_answerer_domain_overview(user):
    cursor = connection.cursor()
    cmd = """SELECT * FROM answerer_overview
             WHERE user_id = %s"""
    cursor.execute(cmd, [user.id])
    return dictfetchall(cursor)

def get_overview_record(user, domain):
    cursor = connection.cursor()
    cmd = """SELECT user_level, price FROM answerer_overview
             WHERE user_id = %s and domain_id = %s"""
    cursor.execute(cmd, [user.id, domain.id])
    res = dictfetchall(cursor)
    return res[0]

def get_global_user_overview():
    cursor = connection.cursor()
    cmd = """ SELECT o.username, o.short_name, o.question_quota, o.accuracy, o.user_level, p.num_pending
              FROM answerer_overview as o
              LEFT JOIN
                 (SELECT a.answerer_id, q.domain_id, COUNT(a.question_id) AS num_pending
                  FROM ui_assignment AS a JOIN ui_basequestion AS q ON a.question_id = q.id
                  WHERE completed = 'f'
                  GROUP BY a.answerer_id, q.domain_id) AS p
              ON p.answerer_id = o.user_id AND p.domain_id = o.domain_id
              ORDER BY o.accuracy DESC, o.short_name"""
    cursor.execute(cmd)
    res = dictfetchall(cursor)
    return res

def get_batch_overview(batch_id):
    cursor = connection.cursor()
    cmd = """ SELECT local_field_name, number_allocated, number_completed, poisson_binomial_conf as conf
              FROM batch_overview as o
              WHERE id = %s"""
    cursor.execute(cmd, (batch_id,))
    return dictfetchall(cursor)

def get_user_level(user, domain):
    return get_overview_record(user, domain)['user_level']

def get_level_dist(question, members):
    """ given a list of members, calculates a histogram of user levels"""
    # TODO: reimplement me!
    pass

#TODO: change this so that a reviewer is only assigned to questions if 
# he or she has not exceeded the weekly question quota
def select_reviewer(domain):
    cursor = connection.cursor()
    domain_id = domain.id
    cmd = """SELECT * FROM answerer_overview
           WHERE user_level = (SELECT MAX(u.level_number) 
                               FROM ui_level u 
                               WHERE domain_id = %s)
             AND domain_id = %s
           ORDER BY random()
           LIMIT 1"""
    cursor.execute(cmd, (domain_id, domain_id,))
    return dictfetchall(cursor)[0]

# def get_allocations(question, sample_size=10, min_size=1, max_size=7):
#     domain_id = question.domain.id
#     cursor = connection.cursor()
#     cmd = """ SELECT poisson_binomial_conf(accuracy) confidence_score,
#                      array_accum(user_id) user_id_set
#               FROM generate_allocs(%s, %s, %s, %s)
#               GROUP BY allocation_id ORDER BY confidence_score DESC;"""
#     cursor.execute(cmd, (domain_id, min_size, max_size, sample_size,))
#     allocations = list()
#     for rec in cursor.fetchall():
#         a = Allocation()
#         a.confidence = rec[0]
#         a.members = rec[1]
#         allocations.append(a)
#     return allocations

# def update_prices(min_size=1, max_size=11, sample_size=1000):
#     cursor = connection.cursor()
#     cmd = "SELECT * FROM get_prices(%s, %s, %s, %s);"
#     domains = Domain.objects.all()
#     for domain in domains:
#         cursor.execute(cmd, (domain.id, min_size, max_size, sample_size,))
#         rec = cursor.fetchone()
#         if rec:
#             prices = rec[0]
#             for x in range(len(prices)):
#                 price = prices[x]
#                 level = Level.objects.get(domain=domain, level_number=x+1)
#                 level.price = price * 10
#                 level.save()
#         else:
#             return False
#     return True

def update_prices():
    domains = ui.models.Domain.objects.all()
    results = {}
    for domain in domains:
        p = StaticPricer(domain.id)
        response = p.calculate_prices()
        prices = response['prices']
        for level in prices:
            level_number = SymbolicUtils.decode_tag(level)
            price = prices[level]
            level = ui.models.Level.objects.get(domain=domain, level_number=level_number)
            level.price = price
            level.save()
            return response

# def get_allocations_by_domain(domain_id, sample_size=10, min_size=1, max_size=7, min_confidence=.50, max_price=1000):
#     cursor = connection.cursor()
#     cmd = """ SELECT poisson_binomial_conf(l.confidence_upper_bound) confidence_score,
#                      array_accum(a.user_id) user_id_set, SUM(a.price) price
#               FROM generate_allocs(%s, %s, %s, %s) as a, ui_level as l
#               GROUP BY allocation_id 
#               HAVING sum(a.price) < %s AND poisson_binomial_conf(l.confidence_upper_bound) > %s"""
#     cursor.execute(cmd, (domain_id, min_size, max_size, sample_size, max_price, min_confidence/100.0))
#     allocations = list()
#     for rec in cursor.fetchall():
#         a = Allocation()
#         a.confidence = rec[0]
#         a.members = rec[1]
#         a.price = rec[2]
#         allocations.append(a)
#     return allocations

def get_allocations_by_domain(domain_id, sample_size=10, min_size=1, max_size=7, min_confidence=50, max_price=1000):
    cursor = connection.cursor()

    cmd = """ SELECT c.confidence_score, array_accum(a.user_id) user_id_set, sum(l.price) price
              FROM allocations AS a, alloc_conf_scores AS c, ui_level as l
              WHERE a.domain_id = %s
                AND c.confidence_score >= %s 
                AND a.allocation_id = c.allocation_id
                AND a.domain_id = c.domain_id
                AND a.user_level = l.level_number
              GROUP BY a.allocation_id, c.confidence_score
              HAVING sum(l.price) < %s
                 AND array_length(array_accum(a.user_id), 1) >= %s
                 AND array_length(array_accum(a.user_id), 1) <= %s
              ORDER BY random()
              LIMIT %s """

    min_confidence /= 100.0
    assert min_confidence <= 1

    vals = (domain_id, min_confidence, max_price, min_size, max_size, sample_size,)
    cursor.execute(cmd, vals)
    allocations = list()
    for rec in cursor.fetchall():
        a = Allocation()
        a.confidence = rec[0]
        a.members = rec[1]
        a.price = rec[2]
        allocations.append(a)
    return allocations

class Allocation:
    confidence = 0
    price = 0
    members = None
    def __unicode__(self):
        return self.members
    
    def get_dict(self):
        rep = dict()
        rep['confidence'] = self.confidence
        rep['price'] = self.price
        rep['members'] = list(self.members)
        return rep
