# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BaseQuestion.batch'
        db.add_column('ui_basequestion', 'batch',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ui.Batch'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'SchemaMapQuestion.batch'
        db.delete_column('ui_schemamapquestion', 'batch_id')


    def backwards(self, orm):
        # Deleting field 'BaseQuestion.batch'
        db.delete_column('ui_basequestion', 'batch_id')


        # User chose to not deal with backwards NULL issues for 'SchemaMapQuestion.batch'
        raise RuntimeError("Cannot reverse this migration. 'SchemaMapQuestion.batch' and its values cannot be restored.")

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
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ui.Batch']", 'null': 'True', 'blank': 'True'}),
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