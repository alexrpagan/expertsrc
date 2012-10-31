# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Feedback'
        db.create_table('ui_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('sentiment', self.gf('django.db.models.fields.IntegerField')()),
            ('improvements', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('ui', ['Feedback'])

        # Adding model 'Domain'
        db.create_table('ui_domain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('ui', ['Domain'])

        # Adding model 'UserProfile'
        db.create_table('ui_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('user_class', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('bank_balance', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('has_been_assigned', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ui', ['UserProfile'])

        # Adding model 'TempAccuracy'
        db.create_table('ui_tempaccuracy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('accuracy', self.gf('django.db.models.fields.FloatField')(default=0.5)),
        ))
        db.send_create_signal('ui', ['TempAccuracy'])

        # Adding model 'Level'
        db.create_table('ui_level', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Domain'])),
            ('level_number', self.gf('django.db.models.fields.IntegerField')()),
            ('confidence_upper_bound', self.gf('django.db.models.fields.FloatField')()),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ui', ['Level'])

        # Adding model 'Expertise'
        db.create_table('ui_expertise', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.UserProfile'])),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Domain'])),
            ('question_quota', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('ui', ['Expertise'])

        # Adding model 'Application'
        db.create_table('ui_application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('db_alias', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ui_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('batch_budget', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('avg_confidence', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('batch_size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('ui', ['Application'])

        # Adding model 'QuestionType'
        db.create_table('ui_questiontype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Application'])),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('question_class', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['contenttypes.ContentType'])),
            ('answer_class', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['contenttypes.ContentType'])),
            ('review_class', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('ui', ['QuestionType'])

        # Adding model 'Batch'
        db.create_table('ui_batch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('source_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('is_allocated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('question_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.QuestionType'])),
            ('budget', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ui', ['Batch'])

        # Adding model 'BaseQuestion'
        db.create_table('ui_basequestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Domain'])),
            ('submit_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('question_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.QuestionType'])),
        ))
        db.send_create_signal('ui', ['BaseQuestion'])

        # Adding model 'BaseChoice'
        db.create_table('ui_basechoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.BaseQuestion'])),
        ))
        db.send_create_signal('ui', ['BaseChoice'])

        # Adding model 'BaseAnswer'
        db.create_table('ui_baseanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.BaseQuestion'])),
            ('answerer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('confidence', self.gf('django.db.models.fields.FloatField')()),
            ('authority', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('ui', ['BaseAnswer'])

        # Adding model 'BaseReview'
        db.create_table('ui_basereview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reviewer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('answer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.BaseAnswer'])),
            ('is_correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feedback', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('confidence', self.gf('django.db.models.fields.FloatField')()),
            ('authority', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('ui', ['BaseReview'])

        # Adding model 'Assignment'
        db.create_table('ui_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answerer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('complete_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.BaseQuestion'])),
            ('agreed_price', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ui', ['Assignment'])

        # Adding model 'ReviewAssignment'
        db.create_table('ui_reviewassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reviewer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('complete_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('answer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.BaseAnswer'])),
            ('agreed_price', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ui', ['ReviewAssignment'])

        # Adding model 'SchemaMapQuestion'
        db.create_table('ui_schemamapquestion', (
            ('basequestion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseQuestion'], unique=True, primary_key=True)),
            ('local_field_id', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('local_field_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Batch'])),
        ))
        db.send_create_signal('ui', ['SchemaMapQuestion'])

        # Adding model 'SchemaMapChoice'
        db.create_table('ui_schemamapchoice', (
            ('basechoice_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseChoice'], unique=True, primary_key=True)),
            ('global_attribute_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('global_attribute_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('confidence_score', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ui', ['SchemaMapChoice'])

        # Adding model 'SchemaMapAnswer'
        db.create_table('ui_schemamapanswer', (
            ('baseanswer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseAnswer'], unique=True, primary_key=True)),
            ('local_field_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('global_attribute_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('is_match', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ui', ['SchemaMapAnswer'])

        # Adding model 'SchemaMapReview'
        db.create_table('ui_schemamapreview', (
            ('basereview_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseReview'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('ui', ['SchemaMapReview'])

        # Adding model 'NRTrainingQuestion'
        db.create_table('ui_nrtrainingquestion', (
            ('basequestion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseQuestion'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('ui', ['NRTrainingQuestion'])

        # Adding model 'NRTrainingChoice'
        db.create_table('ui_nrtrainingchoice', (
            ('basechoice_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseChoice'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('ui', ['NRTrainingChoice'])

        # Adding model 'NRTrainingAnswer'
        db.create_table('ui_nrtraininganswer', (
            ('baseanswer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseAnswer'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('ui', ['NRTrainingAnswer'])

        # Adding model 'NRTrainingReview'
        db.create_table('ui_nrtrainingreview', (
            ('basereview_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ui.BaseReview'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('ui', ['NRTrainingReview'])


    def backwards(self, orm):
        # Deleting model 'Feedback'
        db.delete_table('ui_feedback')

        # Deleting model 'Domain'
        db.delete_table('ui_domain')

        # Deleting model 'UserProfile'
        db.delete_table('ui_userprofile')

        # Deleting model 'TempAccuracy'
        db.delete_table('ui_tempaccuracy')

        # Deleting model 'Level'
        db.delete_table('ui_level')

        # Deleting model 'Expertise'
        db.delete_table('ui_expertise')

        # Deleting model 'Application'
        db.delete_table('ui_application')

        # Deleting model 'QuestionType'
        db.delete_table('ui_questiontype')

        # Deleting model 'Batch'
        db.delete_table('ui_batch')

        # Deleting model 'BaseQuestion'
        db.delete_table('ui_basequestion')

        # Deleting model 'BaseChoice'
        db.delete_table('ui_basechoice')

        # Deleting model 'BaseAnswer'
        db.delete_table('ui_baseanswer')

        # Deleting model 'BaseReview'
        db.delete_table('ui_basereview')

        # Deleting model 'Assignment'
        db.delete_table('ui_assignment')

        # Deleting model 'ReviewAssignment'
        db.delete_table('ui_reviewassignment')

        # Deleting model 'SchemaMapQuestion'
        db.delete_table('ui_schemamapquestion')

        # Deleting model 'SchemaMapChoice'
        db.delete_table('ui_schemamapchoice')

        # Deleting model 'SchemaMapAnswer'
        db.delete_table('ui_schemamapanswer')

        # Deleting model 'SchemaMapReview'
        db.delete_table('ui_schemamapreview')

        # Deleting model 'NRTrainingQuestion'
        db.delete_table('ui_nrtrainingquestion')

        # Deleting model 'NRTrainingChoice'
        db.delete_table('ui_nrtrainingchoice')

        # Deleting model 'NRTrainingAnswer'
        db.delete_table('ui_nrtraininganswer')

        # Deleting model 'NRTrainingReview'
        db.delete_table('ui_nrtrainingreview')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ui.application': {
            'Meta': {'object_name': 'Application'},
            'avg_confidence': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'batch_budget': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'batch_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'db_alias': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'ui_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'ui.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'agreed_price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'answerer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'complete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.BaseQuestion']"})
        },
        'ui.baseanswer': {
            'Meta': {'object_name': 'BaseAnswer'},
            'answerer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'authority': ('django.db.models.fields.FloatField', [], {}),
            'confidence': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.BaseQuestion']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'ui.basechoice': {
            'Meta': {'object_name': 'BaseChoice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.BaseQuestion']"})
        },
        'ui.basequestion': {
            'Meta': {'object_name': 'BaseQuestion'},
            'asker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.QuestionType']"}),
            'submit_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'ui.basereview': {
            'Meta': {'object_name': 'BaseReview'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.BaseAnswer']"}),
            'authority': ('django.db.models.fields.FloatField', [], {}),
            'confidence': ('django.db.models.fields.FloatField', [], {}),
            'feedback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ui.batch': {
            'Meta': {'object_name': 'Batch'},
            'budget': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_allocated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'question_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.QuestionType']"}),
            'source_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'ui.domain': {
            'Meta': {'object_name': 'Domain'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'ui.expertise': {
            'Meta': {'object_name': 'Expertise'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question_quota': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.UserProfile']"})
        },
        'ui.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'improvements': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sentiment': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ui.level': {
            'Meta': {'object_name': 'Level'},
            'confidence_upper_bound': ('django.db.models.fields.FloatField', [], {}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_number': ('django.db.models.fields.IntegerField', [], {}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'ui.nrtraininganswer': {
            'Meta': {'object_name': 'NRTrainingAnswer', '_ormbases': ['ui.BaseAnswer']},
            'baseanswer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseAnswer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'ui.nrtrainingchoice': {
            'Meta': {'object_name': 'NRTrainingChoice', '_ormbases': ['ui.BaseChoice']},
            'basechoice_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseChoice']", 'unique': 'True', 'primary_key': 'True'})
        },
        'ui.nrtrainingquestion': {
            'Meta': {'object_name': 'NRTrainingQuestion', '_ormbases': ['ui.BaseQuestion']},
            'basequestion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseQuestion']", 'unique': 'True', 'primary_key': 'True'})
        },
        'ui.nrtrainingreview': {
            'Meta': {'object_name': 'NRTrainingReview', '_ormbases': ['ui.BaseReview']},
            'basereview_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseReview']", 'unique': 'True', 'primary_key': 'True'})
        },
        'ui.questiontype': {
            'Meta': {'object_name': 'QuestionType'},
            'answer_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Application']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'question_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'review_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'ui.reviewassignment': {
            'Meta': {'object_name': 'ReviewAssignment'},
            'agreed_price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.BaseAnswer']"}),
            'complete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ui.schemamapanswer': {
            'Meta': {'object_name': 'SchemaMapAnswer', '_ormbases': ['ui.BaseAnswer']},
            'baseanswer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseAnswer']", 'unique': 'True', 'primary_key': 'True'}),
            'global_attribute_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'is_match': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'local_field_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'ui.schemamapchoice': {
            'Meta': {'object_name': 'SchemaMapChoice', '_ormbases': ['ui.BaseChoice']},
            'basechoice_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseChoice']", 'unique': 'True', 'primary_key': 'True'}),
            'confidence_score': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'global_attribute_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'global_attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'ui.schemamapquestion': {
            'Meta': {'object_name': 'SchemaMapQuestion', '_ormbases': ['ui.BaseQuestion']},
            'basequestion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseQuestion']", 'unique': 'True', 'primary_key': 'True'}),
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Batch']"}),
            'local_field_id': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'local_field_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'ui.schemamapreview': {
            'Meta': {'object_name': 'SchemaMapReview', '_ormbases': ['ui.BaseReview']},
            'basereview_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ui.BaseReview']", 'unique': 'True', 'primary_key': 'True'})
        },
        'ui.tempaccuracy': {
            'Meta': {'object_name': 'TempAccuracy'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'default': '0.5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ui.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bank_balance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ui.Domain']", 'through': "orm['ui.Expertise']", 'symmetrical': 'False'}),
            'has_been_assigned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'user_class': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['ui']