SET search_path TO public;

-- TODO: need to replace this with a more general overview
-- Specifically: only schemamapquestions have batch id. Either give all questions a 
-- nullable batch_id, or subclass basequestion with batchedquestion....

DROP VIEW IF EXISTS batch_overview;
CREATE OR REPLACE VIEW batch_overview AS
SELECT 
       b.id as batch_id,
       bq.id as question_id,
       sum(case when a.completed = 't' then 1 else 0 end) as number_completed,
       sum(case when a.completed = 't' then a.agreed_price else 0 end) as funds_rendered,
       array_accum(o.accuracy) as user_confs,
       sum(a.agreed_price) as total_price
FROM ui_batch b, ui_assignment a, answerer_overview o, ui_basequestion bq 
WHERE a.question_id = bq.id and bq.batch_id = b.id and o.user_id = a.answerer_id 
GROUP BY b.id, bq.id;

CREATE OR REPLACE FUNCTION get_level_dist(str_probs float[], str_thresh float[]) RETURNS int[] AS
$$
probs = map(float, str_probs[1:-1].split(','))
thresh = map(float, str_thresh[1:-1].split(','))
dist = [0] * len(thresh)
for prob in probs:
    idxs = range(len(thresh))
    idxs.reverse()
    for i in idxs:
        if prob >= thresh[i]:
            dist[i] += 1 
            break
        if i == 0 and prob < thresh[0]:
            dist[0] += 1
return dist
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION thresh_array(int) RETURNS float[] AS
$$         
DECLARE
    domain_id alias for $1;
    res float[];
    cmd text;
    BEGIN
    cmd := 'SELECT array_accum(c) ' ||
           'FROM (SELECT confidence_upper_bound as c ' ||
                  'FROM ui_level WHERE domain_id = ' || domain_id || ' ' ||
                  'ORDER BY level_number ASC) AS i';
    execute cmd into res;
    return res;
END;
$$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS market_snap;
CREATE TABLE market_snap (
    dist int[],
    avails int[],
    prices float[],
    domain_id int,
    time timestamp DEFAULT now()
);
