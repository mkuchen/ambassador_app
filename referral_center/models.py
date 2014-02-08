from django.contrib.auth.models import User
from django.db import models

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.models import CloudinaryField

import urllib
import datetime

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^cloudinary\.models\.CloudinaryField"])

class Member(models.Model):
	user = models.OneToOneField(User)
	display_name = models.CharField(max_length=60, default="Referral Marketing Solutions")
	quote = models.CharField(max_length=300, default="Let's get things rolling!")
	bio = models.TextField(default="")
	profile_image = CloudinaryField("image", default=None, blank=True, null=True)

	def cropped_image(self):
		return self.logo_image.image( width = 150,  height = 150, 
			crop = "thumb", gravity = "face" )



class Referral(models.Model):
	link_title = models.CharField(max_length=500)
	date_submitted = models.DateTimeField(auto_now_add=True)
	logo_image = CloudinaryField("image", default=None, blank=True, null=True)
	banner_image = CloudinaryField("image", default=None, blank=True, null=True)
	banner_text = models.CharField(max_length=1000)
	font_family = models.CharField(max_length=500)

	owner = models.ForeignKey(Member, blank=True, null=True)



class ReferralStat(models.Model):
	latest = models.BooleanField(default=False)
	active = models.BooleanField(default=True)
	date_recorded = models.DateTimeField(blank=True, null=True, default=None)
	
	referral = models.ForeignKey(Referral, blank=True, null=True, default=None)

	num_clicks = models.IntegerField(default=0)
	num_purchases = models.IntegerField(default=0)
	
	def update_counter(self):
		self.num_clicks += 1
		self.save()
		return True

	def update_purchase(self):
		self.num_purchases += 1
		self.save()
		return True

	def get_stats_dict(self):
		stats = {
			'num_clicks': self.num_clicks,
			'num_purchases': self.num_purchases,
			'rate_clickthrough': self.num_purchases/self.num_clicks,
			## ...
		}
		return stats

	def time_since_posted(self):
		return datetime.datetime.now() - self.date_posted


