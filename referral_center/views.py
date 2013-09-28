from vanilla import CreateView, FormView
from django.http import HttpResponseRedirect
from referral_center.models import Referral

class ReferralCreate(CreateView):
	model = Referral

	success_url = "///"
	fields = ['link_title']
