from django.contrib.auth.models import User
from django.db import models

import urllib

class Referral(models.Model):
	link_title = models.CharField(max_length=500)
	clicks = models.IntegerField(default=0)
	owner = models.ForeignKey(User, blank=True, null=True, default=None)
	date_submitted = models.DateTimeField(auto_now_add=True)
	## add header title

	## add catchphrase

	## add banner url

	def update_counter(self):
		self.clicks += 1
		return True


"""
class Referral_Hist(models.Model):
	date = models.DateTimeField('date calculated')
	clicks = models.IntegerField(default=0)
	referral = models.ForeignKey(Referral)
"""