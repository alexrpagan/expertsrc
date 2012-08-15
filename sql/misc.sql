set search_path to public;

-- since the 'num_to_answer' metric, is skewed for fake questions this can be used
-- to place those questions three weeks in the past.

CREATE OR REPLACE FUNCTION time_warp_training_questions() RETURNS void AS
$$
BEGIN
UPDATE ui_basequestion SET submit_time = now()::timestamp - '21 days'::interval
WHERE question_type_id IN (SELECT id 
                           FROM ui_questiontype 
                           WHERE short_name = 'training'); 
END;
$$ LANGUAGE plpgsql;
