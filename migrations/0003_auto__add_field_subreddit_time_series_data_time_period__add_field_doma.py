# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Subreddit_Time_Series_Data.time_period'
        db.add_column(u'reddit_data_subreddit_time_series_data', 'time_period',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_time_series.Time_Period'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Domain_Time_Series_Data.time_period'
        db.add_column(u'reddit_data_domain_time_series_data', 'time_period',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_time_series.Time_Period'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Subreddit_Time_Series_Data.time_period'
        db.delete_column(u'reddit_data_subreddit_time_series_data', 'time_period_id')

        # Deleting field 'Domain_Time_Series_Data.time_period'
        db.delete_column(u'reddit_data_domain_time_series_data', 'time_period_id')


    models = {
        u'django_time_series.time_period': {
            'Meta': {'object_name': 'Time_Period'},
            'aggregate_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_period_category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_period_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'reddit_collect.domain': {
            'Meta': {'object_name': 'Domain'},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_multimedia': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_news': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_self_post': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'long_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'use_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'reddit_collect.subreddit': {
            'Meta': {'object_name': 'Subreddit'},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_utc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_utc_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'header_title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'over_18': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reddit_full_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reddit_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subscribers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'reddit_data.domain_time_series_data': {
            'Meta': {'object_name': 'Domain_Time_Series_Data'},
            'aggregate_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reddit_collect.Domain']", 'null': 'True', 'blank': 'True'}),
            'domain_long_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'downvotes_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'downvotes_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'downvotes_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'filter_1': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_10': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_2': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_3': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_5': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_7': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_8': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_9': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_1': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_10': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_2': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_3': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_4': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_5': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_6': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_7': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_8': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_9': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'num_comments_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'num_comments_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_comments_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'over_18_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'score_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'score_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'score_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'self_post_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_time_series.Time_Period']", 'null': 'True', 'blank': 'True'}),
            'time_period_category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_period_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'upvotes_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'upvotes_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'upvotes_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'reddit_data.subreddit_time_series_data': {
            'Meta': {'object_name': 'Subreddit_Time_Series_Data'},
            'aggregate_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'downvotes_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'downvotes_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'downvotes_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'filter_1': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_10': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_2': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_3': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_5': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_7': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_8': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_9': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_1': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_10': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_2': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_3': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_4': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_5': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_6': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_7': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_8': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_count_9': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'match_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'num_comments_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'num_comments_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_comments_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'over_18_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'score_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'score_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'score_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'self_post_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subreddit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reddit_collect.Subreddit']", 'null': 'True', 'blank': 'True'}),
            'subreddit_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subreddit_reddit_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_time_series.Time_Period']", 'null': 'True', 'blank': 'True'}),
            'time_period_category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_period_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_period_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'upvotes_average': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'upvotes_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'upvotes_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['reddit_data']