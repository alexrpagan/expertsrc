SET search_path TO public;

DROP VIEW IF EXISTS user_base_stats CASCADE;
CREATE VIEW user_base_stats AS
SELECT
  u.username,
  u.id AS user_id,
  d.id AS domain_id,
  e.question_quota,
  d.short_name,
  SUM(CASE
        WHEN q.id IS NULL OR q.domain_id != d.id OR r.id IS NULL
        THEN 0
        ELSE 1
      END) AS num_reviewed,
  SUM(CASE
        WHEN r.is_correct = 't' AND q.domain_id = d.id
        THEN 1
        ELSE 0
      END) AS num_correct,
  SUM(CASE
        WHEN q.id IS NULL OR q.domain_id != d.id
        THEN 0
        ELSE 1
      END) AS num_answered,
  e.question_quota - SUM(CASE WHEN q.submit_time > (now()::timestamp - '7 days'::interval) and q.domain_id = d.id THEN 1 ELSE 0 END) AS num_to_answer
FROM auth_user AS u
LEFT JOIN (
  ui_baseanswer AS a
  LEFT JOIN ui_basereview AS r ON a.id = r.answer_id
  JOIN ui_basequestion AS q ON q.id = a.question_id
) ON u.id = a.answerer_id
JOIN (
  ui_userprofile AS prf
  JOIN (
    ui_expertise AS e
    JOIN ui_domain AS d ON d.id = e.domain_id
  ) ON prf.id = e.user_id
) ON u.id = prf.user_id
WHERE prf.user_class = 'ANS'
GROUP BY u.id, u.username, d.id, d.short_name, e.question_quota;

DROP VIEW IF EXISTS user_num_pending CASCADE;
CREATE VIEW user_num_pending AS
SELECT
  o.user_id,
  o.domain_id,
  (CASE WHEN p.num_pending IS NULL THEN 0 ELSE p.num_pending END) AS num_pending
FROM user_base_stats as o
LEFT JOIN
  (SELECT a.answerer_id, q.domain_id, COUNT(a.question_id) AS num_pending
   FROM ui_assignment AS a JOIN ui_basequestion AS q ON a.question_id = q.id
   WHERE completed = 'f'
   GROUP BY a.answerer_id, q.domain_id) AS p
ON p.answerer_id = o.user_id AND p.domain_id = o.domain_id;

DROP VIEW IF EXISTS user_computed_ability CASCADE;
CREATE VIEW user_computed_ability AS
SELECT i.user_id, i.domain_id, i.accuracy, i.user_level, l.price
FROM
  (SELECT o.user_id, o.domain_id, acc.accuracy, MAX(l.level_number) AS user_level
    FROM user_base_stats AS o
      LEFT JOIN ui_level AS l ON (o.domain_id = l.domain_id),
      ui_tempaccuracy as acc
    WHERE acc.accuracy >= l.confidence_upper_bound
      AND acc.user_id = o.user_id
    GROUP BY o.user_id, o.domain_id, acc.accuracy
    UNION
    SELECT o.user_id, o.domain_id, acc.accuracy, l.level_number
    FROM user_base_stats AS o
      LEFT JOIN ui_level AS l ON o.domain_id = l.domain_id,
         ui_tempaccuracy as acc
    WHERE acc.accuracy < l.confidence_upper_bound
      AND l.level_number =
            (SELECT MIN(level_number)
             FROM ui_level
             WHERE domain_id = o.domain_id)
      AND acc.user_id = o.user_id) as i
  join ui_level AS l ON i.user_level = l.level_number AND i.domain_id = l.domain_id;

DROP VIEW IF EXISTS answerer_overview CASCADE;
CREATE VIEW answerer_overview AS
select o.*, p.num_pending, a.accuracy, a.user_level, a.price
FROM user_base_stats AS o
    JOIN user_num_pending AS p ON o.user_id = p.user_id and o.domain_id = p.domain_id
    JOIN user_computed_ability AS a ON o.user_id = a.user_id AND o.domain_id = a.domain_id
ORDER BY o.short_name, a.accuracy DESC;

 /*CREATE OR REPLACE FUNCTION get_ratio (BIGINT, BIGINT) RETURNS FLOAT AS $$
DECLARE
  num_answered ALIAS FOR $1;
  num_correct ALIAS FOR $2;
BEGIN
RETURN CASE WHEN num_answered = 0 THEN
       .5::FLOAT
       ELSE num_correct::FLOAT/num_answered::FLOAT
       END;
END;
$$ LANGUAGE plpgsql;*/

/*DROP VIEW IF EXISTS answerer_overview_inner2;
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
         o.num_answered, o.num_correct, o.user_id, o.num_reviewed, o.num_to_answer, l.level_number;*/

