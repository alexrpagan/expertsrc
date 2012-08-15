-- SET search_path TO public;

DROP TABLE IF EXISTS message_queue;
CREATE TABLE message_queue (
       seen boolean default false,
       create_time timestamp default now(),
       batch bytea, -- blob containing serialized batch
       message_type integer, -- 1==question, 2==answer. TODO: define enum
       message_subtype varchar -- defined in Type enum in appropriate .proto definition
);


