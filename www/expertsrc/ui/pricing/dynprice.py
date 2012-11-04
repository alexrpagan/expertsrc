import ui
import cPickle as pickle
from django.db import connection, transaction
from shutil import copy2


HISTOFILE = 'usage.pickle'


def update_prices():
    histos = {}
    old_histos = slurp_histo()
    cold_start = True
    if old_histos:
        copy2(HISTOFILE, HISTOFILE + '.bkp')
        cold_start = False
    domains = list(ui.models.Domain.objects.all())
    for domain in domains:
        histo = ui.dbaccess.get_availability_histo(domain.id)
        histos[domain.id] = histo
    burp_histo(histos)
    if cold_start:
        return
    update = get_price_update(old=old_histos, new=histos)
    apply_price_update(update)


def burp_histo(histo):
    with open(HISTOFILE, 'w') as f:
        pickle.dump(histo, f)


def slurp_histo():
    try:
        with open(HISTOFILE) as f:
            try:
                return pickle.load(f)
            except pickle.UnpicklingError, upe:
                raise upe
            except Exception, e:
                raise e
    except IOError:
        # dyn-price is being run for the first time
        return False


def hist_to_ratio(histo):
    ratio = dict(histo)
    normalizer = float(sum(histo.values()))
    for key in histo.keys():
        ratio[key] = float(ratio[key]) / normalizer
    return ratio

"""
def get_price_update(old={}, new={}):
    update = {}
    for domain in old.keys():
        update[domain] = {}
        old_tmp, new_tmp = old[domain], new[domain]
        assert frozenset(old_tmp.keys()).__hash__() == \
               frozenset(new_tmp.keys()).__hash__()
        current = hist_to_ratio(old_tmp - new_tmp)
        desired = hist_to_ratio(new_tmp)
        adj = {}
        for level in current.keys():
            adj[level] = float(desired[level]) / float(current[level])
        update[domain] = adj
        prices = \
            dict((l.level_number, l.price,) \
                 for l in ui.models.Level.objects.filter(domain_id=domain))
        ratio = hist_to_ratio(prices)
        old_ratio = dict(ratio)
        adj = update[domain]
        for l1 in adj:
            for l2 in ratio:
                if l1 != l2 and adj[l1] > 0:
                    ratio[l2] *= adj[l1]
        renormalizer = sum(ratio.values())
        for l in ratio:
            ratio[l] /= float(renormalizer)
#            update[domain][l] = prices[l] * (1 + (ratio[l] - old_ratio[l]))
            update[domain][l] = sum(prices.values()) * ratio[l]
    return update
"""

def get_price_update(old={}, new={}):
    smoothing = .05
    update = {}
    for domain in old.keys():
        update[domain] = {}
        old_tmp, new_tmp = old[domain], new[domain]
        used = old_tmp - new_tmp
        demand_delta = {}
        prices = \
            dict((l.level_number, l.price,) \
                for l in ui.models.Level.objects.filter(domain_id=domain))
        for key in old_tmp.keys():
            if used[key] > 0 and old_tmp[key] > 0:
                demand_delta[key] = float(used[key]) / float(old_tmp[key])
            else:
                demand_delta[key] = 0.
        for key in demand_delta:
            update[domain][key] = prices[key] * (1. + (smoothing * demand_delta[key]))
    return update


@transaction.commit_on_success
def apply_price_update(update):
    for domain in update:
        print update[domain]
        for level_number in update[domain]:
            level = \
                ui.models.Level.objects.get(level_number=level_number, domain_id=domain)
            level.price = update[domain][level_number]
            level.save()
