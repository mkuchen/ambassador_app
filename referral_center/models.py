from django.contrib.auth.models import User
from django.db import models

class Referral(models.Model):
	link_title = models.CharField(max_length=500)
	link_url = models.CharField(max_length=500)
	clicks = models.IntegerField(default=0)
	owner = models.ForeignKey(User, blank=True, null=True, default=None)

"""
class Referral_Hist(models.Model):
	date = models.DateTimeField('date calculated')
	clicks = models.IntegerField(default=0)
	referral = models.ForeignKey(Referral)
"""