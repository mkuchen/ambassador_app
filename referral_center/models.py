from django.contrib.auth.models import User
from django.db import models

import urllib

"""
class Member(models.Model):
	user = models.OneToOneField(User)
	quote = models.CharField(max_length=300, default="Let's get things rolling!")
	bio = models.TextField(default="")
"""

class Referral(models.Model):
	link_title = models.CharField(max_length=500)
	date_submitted = models.DateTimeField(auto_now_add=True)
	logo_url = models.CharField(max_length=1000)
	banner_background_url = models.CharField(max_length=1000)
	banner_text = models.CharField(max_length=1000)
	font_family = models.CharField(max_length=500)

	owner = models.ForeignKey(Member, blank=False, null=False)


class ReferralStat(models.Model):
	num_clicks = models.IntegerField(default=0)
	num_purchases = models.IntegerField(default=0)
	
	## some stat fields
	def update_counter(self):
		self.num_clicks += 1
		return True

	def update_purchase(self):
		self.num_purchases += 1
		return True

	def get_stats_dict(self):
		stats = {
			'num_clicks': self.num_clicks,
			'num_purchases': self.num_purchases,
			'rate_clickthrough': self.num_purchases/self.num_clicks,
			## ...
		}
		return stats

class ReferralHist(models.Model):
	date = models.DateTimeField('date calculated')

	referral = models.ForeignKey(Referral)
	stat = models.OneToOneField(ReferralStat)

