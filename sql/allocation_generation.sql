DROP TABLE IF EXISTS allocations;
CREATE TABLE allocations(
       domain_id integer,
       allocation_id integer,
       user_id integer,
       accuracy float,
       user_level integer
);

DROP TABLE IF EXISTS alloc_conf_scores;
CREATE TABLE alloc_conf_scores (
       domain_id integer,
       allocation_id integer,
       confidence_score float
);

DROP TYPE IF EXISTS gen_domain_allocs_return_type CASCADE;
CREATE TYPE gen_domain_allocs_return_type AS (
       domain_id integer,
       allocation_id integer,
       user_id integer,
       accuracy float,
       user_level integer
);


CREATE OR REPLACE FUNCTION gen_domain_allocs(domain_id integer, min_size integer, max_size integer, just_odds boolean)
RETURNS SETOF gen_domain_allocs_return_type AS
$$
import itertools
get_overview = """ SELECT user_id, accuracy, user_level 
                   FROM answerer_overview
                   WHERE domain_id = %s AND num_to_answer > 0 """
cmd = get_overview % domain_id
rv = plpy.execute(cmd)
alloc_id = -1

if just_odds:
   step_size = 2
else:
   step_size = 1
 
for allocation_size in range(min_size, max_size+1, step_size):
    idxs = itertools.combinations(range(len(rv)), allocation_size)
    for comb in idxs:
    	alloc_id += 1
    	for i in comb:
           yield ( domain_id, alloc_id, rv[i]['user_id'], rv[i]['accuracy'], rv[i]['user_level'])
$$ language plpythonu;

CREATE OR REPLACE FUNCTION create_allocations(min_size integer, max_size integer, just_odds boolean)
RETURNS VOID AS
$$
plpy.execute('TRUNCATE allocations')
rv = plpy.execute('SELECT id from ui_domain')

for x in range(len(rv)):
    domain_id = rv[x]['id']
    cmd = """INSERT INTO allocations
    	     SELECT a.domain_id, a.allocation_id, a.user_id, 
	     	    l.confidence_upper_bound as accuracy, a.user_level
	     FROM gen_domain_allocs(%s, %s, %s, %s) AS a, ui_level AS l 
	     WHERE a.user_level = l.level_number
	     """
    plpy.execute(cmd % (domain_id, min_size, max_size, just_odds))

plpy.execute('TRUNCATE alloc_conf_scores')

cmd = """INSERT INTO alloc_conf_scores
	 SELECT domain_id, allocation_id, poisson_binomial_conf(accuracy) conf 
	 FROM allocations 
	 GROUP BY domain_id, allocation_id"""

plpy.execute(cmd)

$$ language plpythonu;
