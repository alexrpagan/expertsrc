
CREATE OR REPLACE FUNCTION get_prices(integer, integer, integer, integer)
RETURNS setof float8[] AS
$$
BEGIN
	CREATE TEMPORARY TABLE allocs ON COMMIT DROP AS
	SELECT allocation_id, user_id, user_level, accuracy 
	FROM generate_allocs($1, $2, $3, $4);

	CREATE TEMPORARY TABLE histo ON COMMIT DROP AS
	SELECT poisson_binomial_conf(l.confidence_upper_bound) as conf,
	       SUM(CASE WHEN user_level = 1 THEN 1 ELSE 0 END)::int as level_1,
	       SUM(CASE WHEN user_level = 2 THEN 1 ELSE 0 END)::int as level_2,
	       SUM(CASE WHEN user_level = 3 THEN 1 ELSE 0 END)::int as level_3,
	       SUM(CASE WHEN user_level = 4 THEN 1 ELSE 0 END)::int as level_4,
               COUNT(allocation_id) alloc_size
	FROM allocs, ui_level l
	WHERE l.level_number = user_level 
	GROUP BY allocation_id;

	RETURN QUERY 
	       SELECT (madlib.linregr(conf/alloc_size, array[level_1/alloc_size, level_2/alloc_size, level_3/alloc_size, level_4/alloc_size])).coef 
	       	FROM histo;
--		WHERE NOT(level_4 > 0 AND (level_1 + level_2 + level_3) > 0);
END;
$$ LANGUAGE plpgsql;
	

CREATE OR REPLACE FUNCTION 
