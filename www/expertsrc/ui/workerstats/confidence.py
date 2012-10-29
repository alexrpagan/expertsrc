import itertools
import math


def ecc(alloc, choice_limit=2):
    choice_prior = 1. / choice_limit
    choices = range(choice_limit)
    n = len(alloc)

    def get_response_posterior(corr):
        if corr in posterior_memo:
            return posterior_memo[corr]
        prob = 1.
        for idx in xrange(n):
            answerer_conf = alloc[idx]
            if answerer_conf == 1.:
                # hack to prevent div by zero err
                answerer_conf -= 1e-10
            if response[idx] != corr:
                answerer_conf = (1. - answerer_conf) / (choice_limit - 1.)
            prob *= answerer_conf
        posterior_memo[corr] = prob
        return prob

    conf = 0.
    for correct in choices:
        for response in itertools.product(choices, repeat=n):
            posterior_memo = {}
            response_prior = 0.
            for c in choices:
                response_prior += get_response_posterior(c)
            conf += choice_prior * pow(get_response_posterior(correct), 2) / response_prior
    return conf


def pbc(alloc):
    n = len(alloc)
    assert n % 2 == 1
    majority_size = int(math.ceil(n / 2.0))
    conf = 0.
    voters = range(n)
    for consensus in range(majority_size, n + 1):
        for correct_voters in itertools.combinations(voters, consensus):
            incorrect_voters = filter(lambda x: x not in correct_voters, voters)
            cv_prod = iv_prod = 1.
            for c in [alloc[x] for x in correct_voters]:
                cv_prod = cv_prod * c
            for c in [alloc[x] for x in incorrect_voters]:
                iv_prod = iv_prod * (1. - c)
            conf += cv_prod * iv_prod
    return conf
