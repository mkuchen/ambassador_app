from django.contrib.auth.models import User
from django.db import models

import urllib

class Referral(models.Model):
	link_title = models.CharField(max_length=500)
	clicks = models.IntegerField(default=0)
	owner = models.ForeignKey(User, blank=True, null=True, default=None)
	date_submitted = models.DateTimeField(auto_now_add=True)

	def update_counter(self):
		self.clicks += 1
		return True

	@property
	def url_encoded_title(self):
		return urllib.urlencode( {'link': self.link_title} )

	@property
	def url_quoted_title(self):
		return urllib.urlencode(self.link_title)


"""
class Referral_Hist(models.Model):
	date = models.DateTimeField('date calculated')
	clicks = models.IntegerField(default=0)
	referral = models.ForeignKey(Referral)
"""