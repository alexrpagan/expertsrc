import itertools
from cStringIO import StringIO
from collections import Counter
from django.db import connection, transaction
import ui.utils as utils
import ui.workerstats.confidence as cf
import ui.pricing.staticprice as sp
import ui


MAX_SIZE = 10


def conf(allocs):
    return cf.ecc(allocs)


def stringify(x):
    if type(x) == list:
        return '{%s}' % ','.join(map(str, x))
    else:
        return str(x)


@transaction.commit_on_success
def generate_stems(domain, max_size=MAX_SIZE):
    print "domain id: %d" % domain
    stems = []
    levels = dict((l.level_number, l.confidence_upper_bound,)
                   for l in ui.models.Level.objects.filter(domain_id=domain))
    count = 0
    for size in xrange(1, max_size + 1):
        for alloc in itertools.combinations_with_replacement(levels, size):
            # histogram of level numbers in the allocation
            histo = Counter(alloc)
            alloc_confs = [levels[i] for i in alloc]
            dist = []
            for l in levels.keys():
                dist.append(histo[l])
            assert sum(dist) == size
            count += 1
            stems.append((domain, dist, conf(alloc_confs), 0))
            if count % 1000 == 0:
                print "%d generated" % count
    print "generating file"
    string = '\n'.join(['\t'.join(map(stringify, x)) for x in stems])
    stems_file = StringIO(string)
    cur = connection.cursor()
    print "inserting into db"
    cur.copy_from(stems_file, 'alloc_stems', columns=('domain', 'dist', 'conf', 'price'))
    print "done."


# TODO: move this to a SQL file
@transaction.commit_on_success
def create_tables():
    cursor = connection.cursor()
    cmd = """ CREATE TABLE alloc_stems (
                domain INTEGER,
                dist INTEGER[],
                conf NUMERIC,
                price NUMERIC
              ); """
    cursor.execute(cmd)


# TODO: move this to a SQL file
@transaction.commit_on_success
def cleanup():
    cursor = connection.cursor()
    cmd = """ DROP TABLE IF EXISTS alloc_stems; """
    cursor.execute(cmd)


@transaction.commit_on_success
def update_prices(domain):
    cursor = connection.cursor()
    cmd = """ UPDATE alloc_stems SET price = get_price(dist, %s)
              WHERE domain = %s """
    cursor.execute(cmd, (domain, domain))


def run_static_pricing(domain):
    p = sp.StaticPricer(domain)
    response = p.calculate_prices()
    prices = response['prices']
    for level in prices:
        level_number = sp.SymbolicUtils.decode_tag(level)
        price = prices[level]
        level = ui.models.Level.objects.get(domain_id=domain,
                                         level_number=level_number)
        level.price = price
        level.save()


def generate_and_insert(max_size):
    print "dumping tables"
    cleanup()
    print "creating tables"
    create_tables()
    for domain in ui.models.Domain.objects.all():
        print "creating stems"
        generate_stems(domain.id, max_size)
        print "running pricer"
        run_static_pricing(domain.id)
        print "updating prices"
        update_prices(domain.id)


