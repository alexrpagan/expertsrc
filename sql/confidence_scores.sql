create or replace function exhaustive_bayes(str_probs float[]) RETURNS float AS
$$
"""
This is only intended to be used with schemamapping multiple choice questions.

TODO: create good abstractions to that this can be extended to other sorts of
      multiple choice questions
"""

def get_choices():
    """ 
    Retrieves a list of all multiple choice options.
    """
    cmd = """ SELECT c.global_attribute_id as id,
                 c.global_attribute_name as att_name, 
                 SUM(CASE WHEN a.is_match and ba.question_id = bc.question_id 
                          THEN 1 ELSE 0 END) frequency
          FROM ui_schemamapchoice c 
               LEFT JOIN ( 
                  ui_schemamapanswer a
                  JOIN ui_baseanswer ba ON a.baseanswer_ptr_id = ba.id  
               ) ON c.global_attribute_id = a.global_attribute_id
               JOIN ui_basechoice bc ON c.basechoice_ptr_id = bc.id
          GROUP BY c.global_attribute_name, c.global_attribute_id;"""

    rv = plpy.execute(cmd)
    return [rv[i]['id'] for i in xrange(len(rv))]

def seq_generator(alphabet, length):
    import itertools
    return itertools.product(alphabet, repeat=length)

def get_response_confidence(qdata):
    """
    P ( A | R ) * P ( R | A ) * P ( A ) 
    """
    return get_choice_posterior(qdata) * get_response_posterior(qdata) * qdata['choice_prior']

def get_response_prior(qdata):
    """
    P ( R )
    """
    prob = 0.0
    for choice in qdata['choices']:
        prob += get_response_posterior(qdata, choice) * qdata['choice_prior']
    return prob

def get_choice_posterior(qdata):
    """
    P ( A | R )
    """
    return get_response_posterior(qdata) * qdata['choice_prior'] / get_response_prior(qdata)

def get_response_posterior(qdata, corr=None):
    """
    P ( R | A )
    """
    response = qdata['response']
    alloc = qdata['allocation']

    if corr is not None:
        correct_answer = corr
    else:
        correct_answer = qdata['correct_answer']

    prob = 1.0
    for idx in xrange(len(response)):
        answerer_conf = alloc[idx]
        if response[idx] != correct_answer:
            answerer_conf = 1.0 - answerer_conf
        prob = prob * answerer_conf
    return prob

def get_choice_prior(choices):
    """
    P ( A )
    """
    num_choices = len(choices)
    if len > 0:
        return 1.0 / num_choices
    else:
        return 0

def get_confidence_score(allocation, choice_limit):
    qdata = dict()
    qdata['allocation'] = allocation
    qdata['choice_prior'] = 1.0 / choice_limit
    qdata['choices'] = range(choice_limit)
    conf = 0.0
    for correct in qdata['choices']:
        qdata['correct_answer'] = correct
        for response in seq_generator(qdata['choices'], len(allocation)):
            qdata['response'] = response
            conf += get_response_confidence(qdata)
    return conf

# strip brackets from psql array notation
new_str_probs = str_probs[1:-1]

# parse array into list of floats
probs = [float(x) for x in new_str_probs.split(',')]

return get_confidence_score(probs, 2)

$$ LANGUAGE plpythonu;


-- function that computes the probability of a correct majority vote, given an array 
-- representing the accuracy scores of the voters. 
-- warning: this function generates nCr combinations of voters, where n is the number of voters
-- and r is ciel(n/2). thus, it is probably a good idea to only use this function for (very) small
-- values of n.
-- TODO: implement a more efficient version/approximation

CREATE OR REPLACE FUNCTION poisson_binomial(str_probs float[]) RETURNS float AS
$$
import itertools
import math
# strip brackets from psql array notation
new_str_probs = str_probs[1:-1]
# parse array into list of floats
probs = [float(x) for x in new_str_probs.split(',')]
n = len(probs)
majority_size = int(math.ceil(n/2.0))
conf = 0.0
voters = range(len(probs))
for consensus in range(majority_size, n+1):
    for correct_voters in itertools.combinations(voters, consensus):
        incorrect_voters = filter(lambda x: x not in correct_voters, voters)
        cv_prod = 1
        for c in [probs[x] for x in correct_voters]:
            cv_prod = cv_prod * c
        iv_prod = 1
        for c in [probs[x] for x in incorrect_voters]:
            iv_prod = iv_prod * (1 - c)
        conf += cv_prod * iv_prod
return float(conf) 
$$ LANGUAGE plpythonu;

-- an aggregate function that collects the accuracy scores into an array, then applies
-- the confidence calculation to the entire array. It would be much faster to do this incrementally,
-- but the group sizes are generally small, so it is probably not worth the effort to reimplement.

DROP AGGREGATE IF EXISTS poisson_binomial_conf(float) CASCADE;
CREATE AGGREGATE poisson_binomial_conf (
       sfunc = array_append,
       basetype = float,
       stype = float[],
       finalfunc = poisson_binomial,
       initcond = '{}'
);

DROP AGGREGATE IF EXISTS ecc(float) CASCADE;
CREATE AGGREGATE ecc (
    sfunc = array_append,
    basetype = float,
    stype = float[],
    finalfunc = exhaustive_bayes,
    initcond = '{}'
);

DROP AGGREGATE IF EXISTS array_accum(integer) CASCADE;
CREATE AGGREGATE array_accum (
    sfunc = array_append,
    basetype = integer,
    stype = integer[],
    initcond = '{}'
);
