# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Referral'
        db.create_table(u'referral_center_referral', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link_title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('link_url', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('clicks', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'referral_center', ['Referral'])


    def backwards(self, orm):
        # Deleting model 'Referral'
        db.delete_table(u'referral_center_referral')


    models = {
        u'referral_center.referral': {
            'Meta': {'object_name': 'Referral'},
            'clicks': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'link_url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['referral_center']