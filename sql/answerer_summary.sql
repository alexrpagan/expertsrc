SET search_path TO public;

DROP VIEW IF EXISTS answerer_overview_inner CASCADE;
CREATE VIEW answerer_overview_inner AS
SELECT 
u.username, u.id AS user_id, d.id AS domain_id, e.question_quota, d.short_name,
SUM(CASE WHEN q.id IS NULL OR q.domain_id != d.id OR r.id IS NULL THEN 0 ELSE 1 END) AS num_reviewed,
SUM(CASE WHEN r.is_correct = 't' AND q.domain_id = d.id THEN 1 ELSE 0 END) as num_correct,
SUM(CASE WHEN q.id IS NULL OR q.domain_id != d.id THEN 0 ELSE 1 END) AS num_answered,
-- TODO: take another look at this...
e.question_quota - SUM(CASE WHEN q.submit_time > (now()::timestamp - '7 days'::interval) and q.domain_id = d.id THEN 1 ELSE 0 END) AS num_to_answer 
FROM auth_user AS u
LEFT JOIN (
     ui_baseanswer AS a
     LEFT JOIN ui_basereview as r on ( a.id = r.answer_id )
          JOIN ui_basequestion AS q ON ( q.id = a.question_id )
) ON (u.id = a.answerer_id)
JOIN (
      ui_userprofile AS prf
      JOIN (
      	   ui_expertise AS e
	   JOIN ui_domain AS d on d.id = e.domain_id
      ) ON prf.id = e.user_id
) ON u.id = prf.user_id
WHERE prf.user_class = 'ANS'
GROUP BY u.id, u.username, d.id, d.short_name, e.question_quota;	

CREATE OR REPLACE FUNCTION get_ratio (BIGINT, BIGINT) RETURNS FLOAT AS $$
DECLARE
  num_answered ALIAS FOR $1;
  num_correct ALIAS FOR $2;
BEGIN
RETURN CASE WHEN num_answered = 0 THEN 
       .5::FLOAT 
       ELSE num_correct::FLOAT/num_answered::FLOAT
       END;
END;
$$ LANGUAGE plpgsql;

DROP VIEW IF EXISTS answerer_overview_inner2;
CREATE VIEW answerer_overview_inner2 AS
SELECT o.*, get_ratio(o.num_reviewed, o.num_correct) AS accuracy, MAX(l.level_number) AS user_level
FROM answerer_overview_inner AS o LEFT JOIN ui_level AS l ON o.domain_id = l.domain_id
WHERE get_ratio(o.num_reviewed, o.num_correct) >= l.confidence_upper_bound 
GROUP BY o.username, o.domain_id, o.question_quota, o.short_name,
      	 o.num_answered, o.num_correct, o.user_id, o.num_reviewed, o.num_to_answer
UNION
SELECT o.*, get_ratio(o.num_reviewed, o.num_correct) AS accuracy, l.level_number
FROM answerer_overview_inner AS o LEFT JOIN ui_level AS l ON o.domain_id = l.domain_id
WHERE get_ratio(o.num_reviewed, o.num_correct) < l.confidence_upper_bound AND l.level_number = (SELECT MIN(level_number) from ui_level where domain_id = o.domain_id)
GROUP BY o.username, o.domain_id, o.question_quota, o.short_name,
      	 o.num_answered, o.num_correct, o.user_id, o.num_reviewed, o.num_to_answer, l.level_number;

DROP VIEW IF EXISTS answerer_overview_inner3;
CREATE VIEW answerer_overview_inner3 AS
SELECT o.*, l.price AS price
FROM answerer_overview_inner2 AS o, ui_level AS l
WHERE o.user_level = l.level_number;

DROP VIEW IF EXISTS answerer_overview;
CREATE VIEW answerer_overview AS
SELECT o.*, (CASE WHEN p.num_pending IS NULL THEN 0 ELSE p.num_pending END)
FROM answerer_overview_inner3 as o
LEFT JOIN
(SELECT a.answerer_id, q.domain_id, COUNT(a.question_id) AS num_pending
 FROM ui_assignment AS a JOIN ui_basequestion AS q ON a.question_id = q.id
 WHERE completed = 'f'
 GROUP BY a.answerer_id, q.domain_id) AS p
 ON p.answerer_id = o.user_id AND p.domain_id = o.domain_id
 ORDER BY o.accuracy DESC, o.short_name;

