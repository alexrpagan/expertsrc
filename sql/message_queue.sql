DROP TABLE IF EXISTS message_queue;
CREATE TABLE message_queue (
    id SERIAL,
    queue_name TEXT,
    date_created TIMESTAMP DEFAULT now(),
    message BYTEA,
    is_seen BOOLEAN DEFAULT 'f',
    is_complete BOOLEAN DEFAULT 'f'
);


CREATE FUNCTION notify_trigger() RETURNS trigger AS $$
DECLARE
BEGIN
  PERFORM pg_notify('message_queue', TG_TABLE_NAME || ',id,' || NEW.id );
  RETURN new;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER watched_table_trigger AFTER INSERT ON message_queue
FOR EACH ROW EXECUTE PROCEDURE notify_trigger();