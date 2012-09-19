from django.db import connection, transaction
from itertools import izip

import ui
from ui.utils import *
from ui.pricing import *
from ui.models import *

import random
import logging
import itertools
import math

@transaction.commit_on_success
def get_answerer_domain_overview(user):
    cursor = connection.cursor()
    cmd = """ SELECT o.*, o.num_answered + o.num_pending as total_answered 
              FROM answerer_overview as o WHERE user_id = %s """
    cursor.execute(cmd, [user.id])
    return dictfetchall(cursor)

@transaction.commit_on_success
def get_overview_record(user, domain):
    cursor = connection.cursor()
    cmd = """ SELECT user_level, price FROM answerer_overview
              WHERE user_id = %s and domain_id = %s """
    cursor.execute(cmd, [user.id, domain.id])
    res = dictfetchall(cursor)
    return res[0]

@transaction.commit_on_success
def get_global_user_overview():
    cursor = connection.cursor()
    cmd = """ SELECT username, short_name, question_quota, accuracy, user_level, num_pending
              FROM answerer_overview as o
              ORDER BY o.accuracy DESC, o.short_name """
    cursor.execute(cmd)
    res = dictfetchall(cursor)
    return res

@transaction.commit_on_success
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
@transaction.commit_on_success
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

@transaction.commit_on_success
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
        results[domain.id] = response
    return results

def max_conf(domain_id, max_price, number_of_questions):
    """
    For all questions in a batch, select (in order) the allocation having the maximal confidence
    which also has a price lower than the one specified.
    """
    get_frame = """ SELECT confidence_score, user_id_set, price
                    FROM allocs_joined
                    WHERE domain_id = %s
                      AND price < %s
                      AND NOT user_id_set && %s
                    ORDER BY confidence_score DESC
                    OFFSET %s
                    LIMIT %s """

    avg_price = 0
    if number_of_questions:
        avg_price = float(max_price) / number_of_questions

    frame_size = 2 * number_of_questions
    return optimized_alloc_selector(domain_id, get_frame, avg_price, number_of_questions, frame_size)
    
def min_price(domain_id, min_conf, number_of_questions):
    """
    For all questions in a batch, select (in order) the allocation having the minimal price which
    meets the given confidence requirements.
    """
    get_frame = """ SELECT confidence_score, user_id_set, price
                    FROM allocs_joined
                    WHERE domain_id = %s
                      AND confidence_score >= %s
                      AND NOT user_id_set && %s
                    ORDER BY price ASC
                    OFFSET %s
                    LIMIT %s """
    
    frame_size = 2 * number_of_questions
    return optimized_alloc_selector(domain_id, get_frame, min_conf, number_of_questions, frame_size)

@transaction.commit_on_success
def get_avail_answerers(domain_id):
    cursor = connection.cursor()
    # TODO: change so that pending questions are subtracted from num_to_answer

    cmd = """ SELECT o.user_id, o.num_to_answer - o.num_pending
              FROM answerer_overview o
              WHERE o.domain_id = %s """

    vals = (domain_id,)
    cursor.execute(cmd, vals)
    num_available = {}
    for rec in cursor.fetchall():
        num_available[rec[0]] = rec[1] 
    return num_available

@transaction.commit_on_success
def optimized_alloc_selector(domain_id, get_frame_cmd, constraint, number_of_questions, frame_size):
    # TODO: acquire mutex here...     
    num_available = get_avail_answerers(domain_id)
    cursor = connection.cursor()
    frame = []
    alloc = []
    tapped_out = set()
    curr_question = 0
    frame_position = 0
    workers_left = 0

    for key in num_available.keys():
        if num_available[key] == 0:
            tapped_out.add(key)
        else:
            workers_left += num_available[key]

    offset = 0
    while True: 
        if curr_question == number_of_questions:
            # we've answered all the questions
            break

        questions_left = number_of_questions - curr_question
        if workers_left < questions_left:
            # not enough workers to allocate the rest of the questions
            return []

        if frame_position == len(frame):
            parms = (domain_id, constraint, list(tapped_out), offset, frame_size,)
            cursor.execute(get_frame_cmd, parms)
            frame = dictfetchall(cursor)
            offset += frame_size
            if len(frame) < frame_size and len(frame) < questions_left:
                # not enough allocations to assign to the rest of the questions
                return []
            frame_position = 0

        #try to allocate question
        res_wrk_cpy = dict(num_available)
        a = frame[frame_position]
        has_the_goods = True

        for user_id in a['user_id_set']:
            if res_wrk_cpy[user_id] > 0:
                res_wrk_cpy[user_id] -= 1
                workers_left -= 1
            else:
                tapped_out.add(user_id)
                has_the_goods = False
                break

        if has_the_goods:
            new_alloc = Allocation()
            new_alloc.confidence=a['confidence_score']
            new_alloc.price=a['price']
            new_alloc.members=a['user_id_set']
            curr_question += 1
            alloc.append(new_alloc)
            num_available = dict(res_wrk_cpy)
        else:
            frame_position += 1

    return alloc


@transaction.commit_on_success
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
