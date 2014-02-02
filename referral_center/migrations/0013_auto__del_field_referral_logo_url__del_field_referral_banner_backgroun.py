# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Referral.logo_url'
        db.delete_column(u'referral_center_referral', 'logo_url')

        # Deleting field 'Referral.banner_background_url'
        db.delete_column(u'referral_center_referral', 'banner_background_url')

        # Adding field 'Referral.logo_image'
        db.add_column(u'referral_center_referral', 'logo_image',
                      self.gf('cloudinary.models.CloudinaryField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Referral.banner_image'
        db.add_column(u'referral_center_referral', 'banner_image',
                      self.gf('cloudinary.models.CloudinaryField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Referral.logo_url'
        db.add_column(u'referral_center_referral', 'logo_url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Adding field 'Referral.banner_background_url'
        db.add_column(u'referral_center_referral', 'banner_background_url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Deleting field 'Referral.logo_image'
        db.delete_column(u'referral_center_referral', 'logo_image')

        # Deleting field 'Referral.banner_image'
        db.delete_column(u'referral_center_referral', 'banner_image')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'referral_center.member': {
            'Meta': {'object_name': 'Member'},
            'bio': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'display_name': ('django.db.models.fields.CharField', [], {'default': "'Referral Marketing Solutions'", 'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile_image': ('cloudinary.models.CloudinaryField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'quote': ('django.db.models.fields.CharField', [], {'default': '"Let\'s get things rolling!"', 'max_length': '300'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'referral_center.referral': {
            'Meta': {'object_name': 'Referral'},
            'banner_image': ('cloudinary.models.CloudinaryField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'banner_text': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'font_family': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'logo_image': ('cloudinary.models.CloudinaryField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['referral_center.Member']", 'null': 'True', 'blank': 'True'})
        },
        u'referral_center.referralhist': {
            'Meta': {'object_name': 'ReferralHist'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referral': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['referral_center.Referral']"}),
            'stat': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['referral_center.ReferralStat']", 'unique': 'True'})
        },
        u'referral_center.referralstat': {
            'Meta': {'object_name': 'ReferralStat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_clicks': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_purchases': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['referral_center']