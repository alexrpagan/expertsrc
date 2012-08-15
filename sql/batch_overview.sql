SET search_path TO public;

-- TODO: need to replace this with a more general overview
-- Specifically: only schemamapquestions have batch id. Either give all questions a 
-- nullable batch_id, or subclass basequestion with batchedquestion....

DROP VIEW IF EXISTS batch_overview;
CREATE OR REPLACE VIEW batch_overview AS
SELECT 
       b.id,
       q.basequestion_ptr_id question_id,
       q.local_field_name,
       count(a) number_allocated,
       sum(case when a.completed = 't' then 1 else 0 end) number_completed,
       poisson_binomial_conf(o.accuracy) 
FROM ui_batch b, ui_schemamapquestion q, ui_assignment a, answerer_overview as o
WHERE a.question_id = q.basequestion_ptr_id and 
      q.batch_id = b.id and o.user_id = a.answerer_id 
GROUP BY q.local_field_name, q.basequestion_ptr_id, b.id
ORDER BY b.id, q.basequestion_ptr_id, q.local_field_name;


