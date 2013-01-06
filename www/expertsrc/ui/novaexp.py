import logging
from ui.models import *
from ui.utils import dictfetchall
from django.contrib.auth.models import User
from django.db import connections, transaction
from django.conf import settings


logger = logging.getLogger(__name__)


def alert(msg):
    logger.info(msg)


def f2c(x):
    if x > 1.0: x = 1.0
    if x < 0.0: x = 0.0
    c = hex(int(255*x))[2:]
    if len(c) == 1:
        c = '0' + c
    return c


class GuruType:

    def __init__():
        self.RESP_SCI = 1
        self.SCI = 2
        self.DOMAIN_LEVEL_1 = 3
        self.DOMAIN_LEVEL_2 = 4
        self.GLOBAL = 5


class TestGroup:

    def __init__():
        self.domain = None
        self.datasources = {}  # map data source to a list of gurus
        self.users = []


class CrowdMarket:

    max_per_batch = 20
    ask_code = 'ASK'
    ans_code = 'ANS'
    app_name = 'data-tamer'
    db_alias = settings.TAMER_DB
    ui_url = settings.TAMER_URL
    qt_app_label = 'ui'
    qt_longname = 'Schema Mapping Questions'
    qt_shortname = 'schemamap'
    qt_question_class = 'schemamapquestion'
    qt_answer_class = 'schemamapanswer'
    qt_review_class = 'schemamapreview'
    levels = {1: .7, 2: .8, 3: .9, 4: 1}
    asker_budget = 100
    asker_name = 'data-tamer'
    question_quota = 10
    default_pass = 'test'

    asker = None
    qt = None
    app = None

    @transaction.commit_on_success
    def __init__(self, from_scratch=False):
        if from_scratch:
            print 'cleaning up'
            self.cleanup()
            print 'creating domains'
            self.create_domains()
            print 'creating users'
            self.create_users()
            print 'creating application record'
            self.create_application()
            print 'creating question type record'
            self.create_question_type()
            print 'creating initial asker'
            self.create_asker()
            print 'done'
        else:
            a = User.objects.get(username=self.asker_name)
            self.asker = a
            qt = QuestionType.objects.get(short_name=self.qt_shortname)
            self.qt = qt
            app = Application.objects.get(name=self.app_name)
            self.app = app

    def create_users(self):
        cmd = ''' select hr_521, email_addr, domain, level, is_asker
                  from nova_raw.users '''
        cur = connections[settings.TAMER_DB].cursor()
        cur.execute(cmd)
        for rec in cur.fetchall():
            hr_521, email_addr, domain, level, is_asker = rec
            print hr_521
            u = User.objects.create_user(hr_521, email_addr, self.default_pass)
            u.save()
            p = UserProfile(user=u,
                            user_class=self.ask_code if is_asker else self.ans_code,
                            bank_balance=0)
            p.save()
            if not is_asker:
                temp_acc = TempAccuracy(user=u, accuracy=self.levels[level])
                temp_acc.save()
                domain = Domain.objects.get(short_name=domain)
                e = Expertise(user=p, domain=domain, question_quota=self.question_quota)
                e.save()

    def create_domains(self):
        # get list of domains from database
        cmd = ''' SELECT department_name, department_code
                    FROM nova_raw.departments '''
        cur = connections[settings.TAMER_DB].cursor()
        cur.execute(cmd)
        for rec in cur.fetchall():
            dept_name, dept_code = rec
            d = Domain()
            d.short_name = dept_code
            d.long_name = dept_name
            d.description = ''
            d.save()
            # create levels
            levels = self.levels
            for key in levels:
                level = Level(domain=d,
                              level_number=key,
                              confidence_upper_bound=levels[key])
                level.save()

    def create_application(self):
        app = Application()
        app.name = self.app_name
        app.db_alias = self.db_alias
        app.ui_url = self.ui_url
        app.save()
        self.app = app

    def create_question_type(self):
        qt = QuestionType()
        qt.long_name = self.qt_longname
        qt.short_name = self.qt_shortname
        qt.app = self.app
        qt.question_class = \
            ContentType.objects.get(app_label=self.qt_app_label, \
                                    model=self.qt_question_class)
        qt.answer_class = \
            ContentType.objects.get(app_label=self.qt_app_label, \
                                    model=self.qt_answer_class)
        qt.review_class = \
            ContentType.objects.get(app_label=self.qt_app_label, \
                                    model=self.qt_review_class)
        qt.save()
        self.qt = qt

    def create_asker(self):
        asker = User.objects.create_user(self.asker_name, '', self.default_pass)
        asker.save()
        profile = UserProfile(user=asker,
                              user_class=self.ask_code,
                              bank_balance=self.asker_budget)
        profile.save()
        self.asker = asker

    def map_source(self, source_id):
        cur = connections[settings.TAMER_DB].cursor()
        cmd0 = '''SELECT count(d.*) > 0 as check
                  FROM local_data d
                    JOIN local_fields f ON d.field_id = f.id
                  WHERE f.source_id = %s;'''
        cur.execute(cmd0, (source_id,))
        try:
            assert cur.fetchone()[0]
        except AssertionError:
            alert('source lacks either data or fields')
            return
        cmd1 = '''SELECT preprocess_source(%s);'''
        cmd2 = '''SELECT preprocess_global();'''
        cmd3 = '''SELECT qgrams_results_for_source(%s);
                  SELECT ngrams_results_for_source(%s);
                  SELECT mdl_results_for_source(%s);
                  SELECT nr_composite_load();'''
        alert('preprocessing source %s' % source_id)
        cur.execute(cmd1, (source_id,))
        alert('rebuilding global schema mapping models')
        cur.execute(cmd2)
        alert('mapping source')
        cur.execute(cmd3, (source_id, source_id, source_id))

    def get_field_mappings_by_source(self, source_id, only_unmapped=False):
        """ Retrieves all possible mappings for all fields in a source."""
        cur = connections[settings.TAMER_DB].cursor()
        fields = dict()
        cmd = '''SELECT lf.id, lf.local_name, ama.global_id, ga.name,
                        ama.who_created
                   FROM local_fields lf
              LEFT JOIN attribute_mappings ama
                     ON lf.id = ama.local_id
              LEFT JOIN global_attributes ga
                     ON ama.global_id = ga.id
                  WHERE lf.source_id = %s'''
        cur.execute(cmd, (source_id,))

        for rec in cur.fetchall():
            fid, fname, gid, gname, who = rec
            fields.setdefault(fid, {'id': fid, 'name': fname})
            if gid is not None and who is not None:
                fields[fid]['match'] = {
                    'id': gid, 'name': gname, 'who_mapped': who,
                    'is_mapping': True, 'score': 2.0}

        cmd = '''SELECT lf.id, lf.local_name, nnr.match_id, ga.name, nnr.score
                   FROM nr_ncomp_results_tbl nnr, global_attributes ga,
                        local_fields lf
                  WHERE nnr.field_id = lf.id
                    AND nnr.source_id = %s
                    AND nnr.match_id = ga.id
                    AND (lf.n_values > 0 OR 1 = 1)
               ORDER BY score desc;'''

        cur.execute(cmd, (source_id,))
        records = cur.fetchall()

        for rec in records:
            fid, fname, gid, gname, score = rec
            fields[fid].setdefault('match', {
                'id': gid, 'name': gname, 'score': score,
                'green': f2c(score / 1.0), 'red': f2c(1.0 - score / 2.0)})

            matches = fields[fid].setdefault('matches', list())
            matches.append({'id': gid, 'name': gname, 'score': score,
                            'green': f2c(score / 1.0), 'red': f2c(1.0 - score / 2.0)})

        for fid in fields:
            if 'match' not in fields[fid]:
                fields[fid]['match'] = {'id': 0, 'name': 'Unknown', 'score': 0, 'green': f2c(0), 'red': f2c(1)}
                fields[fid]['matches'] = list()

        to_del = []
        if only_unmapped:
            for fid in fields:
                if 'who_mapped' in fields[fid]['match']:
                    to_del.append(fid)
            for fid in to_del:
                del fields[fid]

        return fields

    @transaction.commit_on_success
    def register_schema_map(self, sourceid, domain_shortname='IT'):
        cur = connections[settings.TAMER_DB].cursor()
        mappings = self.get_field_mappings_by_source(sourceid, only_unmapped=True)
        cmd = "SELECT id, name FROM global_attributes"
        cur.execute(cmd)
        cur.connection.commit()
        global_attributes = dictfetchall(cur)
        batch_rec = Batch()
        batch_rec.owner = self.asker
        batch_rec.question_type = self.qt
        batch_rec.source_name = str(sourceid)
        batch_rec.save()
        for fid in mappings.keys():
            smq = SchemaMapQuestion()
            smq.batch = batch_rec
            smq.asker = batch_rec.owner
            smq.domain = Domain.objects.get(short_name=domain_shortname)
            smq.question_type = self.qt
            smq.local_field_id = fid
            smq.local_field_name = mappings[fid]['name']
            smq.save()
            choices = mappings[fid]['matches']
            ids = list()
            choice_count = 10
            for c in choices:
                if choice_count > 0:
                    smc = SchemaMapChoice()
                    smc.question = smq
                    smc.global_attribute_id = c['id']
                    smc.global_attribute_name = c['name']
                    smc.confidence_score = c['score']
                    smc.save()
                    ids.append(c['id'])
                    choice_count -= 1
            id_set = set(ids)
            for a in global_attributes:
                if a['id'] not in id_set:
                    smc = SchemaMapChoice()
                    smc.question = smq
                    smc.global_attribute_id = a['id']
                    smc.global_attribute_name = a['name']
                    smc.save()

    def allocate_questions(self, username, questions):
        user = User.objects.get(username=username)
        for question in questions:
            a = Assignment(answerer=user, question=question)
            a.save()

    def clear_out_questions(self):
        Batch.objects.all().delete()

    def cleanup(self):
        User.objects.all().delete()
        Domain.objects.all().delete()
        Application.objects.all().delete()

    def test_source(self, source):
        self.map_source(source)
        self.register_schema_map(source)
        self.allocate_questions('GUMPPWO1', BaseQuestion.objects.all())
