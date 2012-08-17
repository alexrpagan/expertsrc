"""
Crude concurrent confidence score implementation.
"""
import psycopg2
import psycopg2.pool
import threading
import multiprocessing

# settings for the input table
CONF_FUNCTIONS = ['ecc', 'poisson_binomial_conf']
FUNC_NO = 0 
DOMAIN_ID = 25
TOTAL_NUMBER = 27894

# (1 / REDUNDANCY_FACTOR) of total cores are used
# TODO: rename this
REDUNDANCY_FACTOR = 2

# psycopg2 connection information
DBNAME = 'expertsrc' 
USER = 'apagan'
PASS = ''
HOST = ''

class DBThread(threading.Thread):
    job_no = None
    cmd = None
    pool = None

    def __init__(self, job_no, cmd, pool):
        threading.Thread.__init__(self)
        self.job_no = job_no
        self.cmd = cmd
        self.pool = pool

    def run(self):
        conn = self.pool.getconn()
        print 'starting job # %d' % self.job_no
        cursor = conn.cursor()
        cursor.execute(self.cmd)
        conn.commit()
        print 'finished job # %d' % self.job_no
        self.pool.putconn(conn)

def create_cmd(job_no, domain_id, max_alloc_id, min_alloc_id, func_no):
    cmd = """ DROP TABLE IF exists alloc_conf_scores_%s;
              CREATE TABLE alloc_conf_scores_%s (
                  domain_id integer,
                  allocation_id integer,
                  confidence_score float
              );
              INSERT INTO alloc_conf_scores_%s (domain_id, allocation_id, confidence_score) 
              SELECT domain_id,
                     allocation_id,
                     %s(accuracy) AS confidence_score
              FROM allocations
              WHERE domain_id = %s
                AND allocation_id > %s
                AND allocation_id <= %s
              GROUP BY domain_id, allocation_id; """
    return cmd % ((job_no,) * 3 + (CONF_FUNCTIONS[func_no], domain_id, min_alloc_id, max_alloc_id,))

def get_data_tables():
    tables = []
    for x in xrange(get_number_of_partitions()):
        tables.append('alloc_conf_scores_%s' % x)
    return tables

def merge_data_tables(pool):
    print 'merging partition tables...'
    tables = get_data_tables()
    select_tmpl = 'SELECT domain_id, allocation_id, confidence_score FROM %s'
    tmpls = [select_tmpl % table for table in tables]
    union_cmd = ' UNION '.join(tmpls)
    final_cmd = 'INSERT INTO alloc_conf_scores %s' % union_cmd
    conn = pool.getconn()
    cursor = conn.cursor()
    cursor.execute(final_cmd)
    conn.commit()
    pool.putconn(conn)

def init_db(pool):
    print 'dropping data in alloc_conf_scores...'
    cmd = 'TRUNCATE alloc_conf_scores;'
    conn = pool.getconn()
    cursor = conn.cursor()
    cursor.execute(cmd)
    conn.commit()
    pool.putconn(conn)

def clean_up_db(pool):
    print 'dropping partition tables...'
    tables = get_data_tables()
    delete_tmpl = 'DROP TABLE IF exists %s;'
    cmd = ''.join([delete_tmpl % table for table in tables])
    conn = pool.getconn()
    cursor = conn.cursor()
    cursor.execute(cmd)
    conn.commit()
    pool.putconn(conn)

def get_number_of_partitions():
    cores = multiprocessing.cpu_count()
    factor = REDUNDANCY_FACTOR
    assert cores >= factor
    assert cores % factor == 0
    # don't want to take down the whole machine.
    return cores / factor

def create_partitions(set_size, part_num):
    import math
    part_size = math.ceil(set_size/float(part_num))
    lower = upper = 0
    for x in xrange(part_num):
        lower = x * part_size
        upper = (x + 1) * part_size
        yield (lower, upper,)
    
def main():
    job_info = []
    part_num = get_number_of_partitions()
    parts = list(create_partitions(TOTAL_NUMBER, part_num))

    func_no = FUNC_NO

    for x in xrange(len(parts)):
        part = parts[x]
        cmd = create_cmd(job_no=x,
                         domain_id=DOMAIN_ID, 
                         min_alloc_id=part[0], 
                         max_alloc_id=part[1],
                         func_no=func_no)
        job_info.append((x, cmd,))

    # not a -real- thread pool
    thread_pool = []

    conn_pool = psycopg2.pool.ThreadedConnectionPool(minconn=part_num, 
                                                     maxconn=part_num,
                                                     database=DBNAME,
                                                     user=USER,
                                                     password=PASS,
                                                     host=HOST)
    init_db(conn_pool)

    for info in job_info:
        thread_pool.append(DBThread(job_no=info[0], cmd=info[1], pool=conn_pool))
    
    for thread in thread_pool:
        thread.start()
        
    for thread in thread_pool:
        thread.join()
    
    merge_data_tables(conn_pool)

    clean_up_db(conn_pool)

if __name__ == "__main__":
    main()

