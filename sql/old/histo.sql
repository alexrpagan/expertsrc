select poisson_binomial_conf(accuracy),
       SUM(CASE WHEN user_level = 1 THEN 1 ELSE 0 END),
       SUM(CASE WHEN user_level = 2 THEN 1 ELSE 0 END),
       SUM(CASE WHEN user_level = 3 THEN 1 ELSE 0 END),
       SUM(CASE WHEN user_level = 4 THEN 1 ELSE 0 END)
from temp_allocs
group by allocation_id;
