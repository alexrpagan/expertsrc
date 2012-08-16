create or replace function exhaustive_bayes(str_probs float[]) RETURNS float AS
$$
import itertools

def get_choices():
    """ 
    Retrieves a list of all multiple choice options.
    """
    pass

def get_priors():
    """ 
    The prior probabilities of each of the multiple choice options.
    """
    pass


#TODO use itertools product instead...

def generate_sequences(alphabet, length):
    seqs = []
    if length == 1:
        for char in alphabet:
            seqs.append([char])
    elif length > 1:
        for char in alphabet:
            for seq in generate_sequences(alphabet, length - 1):
                seqs.append([char] + seq)
    return seqs

def get_response_confidence():
    """
    P ( A | R ) * P ( R | A ) * P ( A ) 
    """
    return get_choice_posterior() * get_response_posterior() * get_choice_prior()

def get_choice_posterior(response, allocation, choices):
    """
    P ( A | R )
    """
    pass

def get_response_posterior():
    """
    P ( R | A )
    """
    pass

def get_choice_prior():
    """
    P ( A )
    """
    pass

def get_confidence_score(allocation, db_data):
    choices = range(10)
    cum_conf = 0
    for answer in generate_sequences(choices, len(allocation)):
        cum_conf += get_reponse_confidence()
    return cum_conf

# get question type model, then call type.get_confidence_score to execute
# the appropriate implementation of the confidence algorithm

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

DROP AGGREGATE IF EXISTS array_accum(integer) CASCADE;
CREATE AGGREGATE array_accum (
    sfunc = array_append,
    basetype = integer,
    stype = integer[],
    initcond = '{}'
);
