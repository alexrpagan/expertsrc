set search_path to public;

CREATE OR REPLACE FUNCTION all_gte(int[], int[]) RETURNS boolean AS
$$
DECLARE
    left alias for $1;
    right alias for $2;
BEGIN
FOR i in 1 .. array_upper(left,1)
LOOP
    if left[i] < right [i] then
        return false;
    end if;
END LOOP;
return true;
END;
$$ LANGUAGE plpgsql;

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
