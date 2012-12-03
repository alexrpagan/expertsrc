SET search_path TO public;

DROP AGGREGATE IF EXISTS array_accum(float) CASCADE;
CREATE AGGREGATE array_accum (
    sfunc = array_append,
    basetype = float,
    stype = float[],
    initcond = '{}'
);

CREATE OR REPLACE FUNCTION get_price(int[], int) RETURNS float AS
$$
DECLARE
    histo alias for $1;
    domain_id alias for $2;
    prices float[];
    result float;
    BEGIN
    result := 0;
    prices := price_array(domain_id);
    FOR i in 1 .. array_upper(histo,1)
    LOOP
        result := result + (histo[i] * prices[i]);
    END LOOP;
    return result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION price_array(int) RETURNS float[] AS
$$
DECLARE
    domain_id alias for $1;
    res float[];
    cmd text;
    BEGIN
    cmd := 'SELECT array_accum(price) ' ||
           'FROM (SELECT price ' ||
                  'FROM  ui_level WHERE domain_id = ' || domain_id || ' ' ||
                  'ORDER BY level_number ASC) AS i';
    execute cmd into res;
    return res;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_stems(int) RETURNS void AS
$$
DECLARE
    domain_id alias for $1;
    cmd text;
    BEGIN
    cmd := 'UPDATE alloc_stems ' ||
           'SET price = get_price(dist,' || domain_id || ')' ||
           'WHERE domain = ' || domain_id ;
    PERFORM cmd;
END;
$$ LANGUAGE plpgsql;

