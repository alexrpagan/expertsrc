# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
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
            ('bank_balance', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('ui', ['UserProfile'])

        # Adding model 'Level'
        db.create_table('ui_level', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Domain'])),
            ('level_number', self.gf('django.db.models.fields.IntegerField')()),
            ('confidence_upper_bound', self.gf('django.db.models.fields.FloatField')()),
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

        # Adding model 'Question'
        db.create_table('ui_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Domain'])),
            ('submit_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('entityid', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('ui', ['Question'])

        # Adding model 'Choice'
        db.create_table('ui_choice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Question'])),
            ('entityid', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('ui', ['Choice'])

        # Adding model 'Answer'
        db.create_table('ui_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answerer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Question'])),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Choice'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_match', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('confidence', self.gf('django.db.models.fields.FloatField')()),
            ('authority', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('ui', ['Answer'])

        # Adding model 'Review'
        db.create_table('ui_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reviewer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('answer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Answer'])),
            ('is_correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feedback', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('ui', ['Review'])

        # Adding model 'Assignment'
        db.create_table('ui_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answerer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Question'])),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('complete_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('ui', ['Assignment'])


    def backwards(self, orm):
        # Deleting model 'Domain'
        db.delete_table('ui_domain')

        # Deleting model 'UserProfile'
        db.delete_table('ui_userprofile')

        # Deleting model 'Level'
        db.delete_table('ui_level')

        # Deleting model 'Expertise'
        db.delete_table('ui_expertise')

        # Deleting model 'Question'
        db.delete_table('ui_question')

        # Deleting model 'Choice'
        db.delete_table('ui_choice')

        # Deleting model 'Answer'
        db.delete_table('ui_answer')

        # Deleting model 'Review'
        db.delete_table('ui_review')

        # Deleting model 'Assignment'
        db.delete_table('ui_assignment')


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
        'ui.answer': {
            'Meta': {'object_name': 'Answer'},
            'answerer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'authority': ('django.db.models.fields.FloatField', [], {}),
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Choice']"}),
            'confidence': ('django.db.models.fields.FloatField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_match': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Question']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'ui.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'answerer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'complete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Question']"})
        },
        'ui.choice': {
            'Meta': {'object_name': 'Choice'},
            'entityid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Question']"})
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
        'ui.level': {
            'Meta': {'object_name': 'Level'},
            'confidence_upper_bound': ('django.db.models.fields.FloatField', [], {}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'ui.question': {
            'Meta': {'object_name': 'Question'},
            'asker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Domain']"}),
            'entityid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submit_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'ui.review': {
            'Meta': {'object_name': 'Review'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Answer']"}),
            'feedback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ui.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bank_balance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ui.Domain']", 'through': "orm['ui.Expertise']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'user_class': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['ui']