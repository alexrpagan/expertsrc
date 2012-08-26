
DROP TABLE IF EXISTS allocation_lock;
CREATE TABLE allocation_lock (
       access_time timestamp,
       user_id bigint
);
