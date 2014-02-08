from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from referral_center.models import Referral, ReferralHist, ReferralStat
import datetime

class Command(BaseCommand):
	args = ''
	help = 'saves ReferralHist models for historicl tracking, repeats hourly'

	def handle(self, *args, **options):
		all_referrals = Referral.objects.all()
		for referral in all_referrals: # for each referral
			# get most recent Hist object and corresponding Stat
			try:
				last_recorded_stat = ReferralStat.objects.get(referral=referral, latest=True)
			except ObjectDoesNotExist:
				self.stdout.write('Error, was not able to find last recorded ReferralStat object for "%s".  Creating now.' % referral.link_title)
				last_recorded_stat = ReferralStat.objects.create(referral=referral, latest=True, active=False, date_recorded=datetime.datetime.now())
			
			try:
				old_active_stat = ReferralStat.objects.get(referral=Referral, active=True)
			except ObjectDoesNotExist:
				self.stdout.write('Error, was not able to find active active ReferralStat object for "%s".  Creating now.' % referral.link_title)
				old_active_stat = ReferralStat.objects.create(referral=referral, latest=False, active=True)

			# create new active referralstat object
			new_active_stat = ReferralStat.objects.create(
												referral=referral,
												num_clicks=last_recorded_stat.num_clicks,
												num_purchases=last_recorded_stat.num_purchases,
											)

			# make the previously active referralstat object not active, but now latest recorded
			old_active_stat.active = False
			old_active_stat.latest = True
			old_active_stat.date_recorded = datetime.datetime.now()
			old_active_stat.save()

			# set the previously latest recorded stat to normal again
			last_recorded_stat.latest = False
			last_recorded_stat.save()

			self.stdout.write('Successfully updated referral "%s"' % referral.link_title)

