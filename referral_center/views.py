from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse, resolve
from django import http
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from referral_center.forms import AdminLinkForm, LinkForm, CreateUserForm, UpdateMemberForm
from referral_center.models import Referral, ReferralStat, ReferralHist, Member
from vanilla import CreateView, FormView, TemplateView, GenericView, DetailView, RedirectView, UpdateView
from ambassador_app.mixins import *
from braces.views import AjaxResponseMixin, JSONResponseMixin

import sys
import datetime
import urllib
import json


class OrderListJson(BaseDatatableView):
	# The model we're going to show
	model = ReferralHist

	# define the columns that will be returned
	columns = ['referral.link_title', 'stat.num_clicks', 'referral.date_submitted', 'referral.owner.user.username', 'referral.id', 'referral.date_submitted']

	# define column names that will be used in sorting
	# order is important and should be same as order of columns
	# displayed by datatables. For non sortable columns use empty
	# value like ''
	order_columns = ['referral.link_title', 'stat.num_clicks', 'referral.date_submitted', '', '']

	# set max limit of records returned, this is used to protect our site if someone tries to attack our site
	# and make it return huge amount of data
	max_display_length = 500

	def get_initial_queryset(self):
		return ReferralHist.objects.filter(referral__owner__user=self.request.user)

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			json_data.append([
				'<a href="/landing/%s/">%s</a>' % (item.referral.link_title, item.referral.link_title),
				item.stat.num_clicks,
				item.referral.date_submitted.strftime("%B %d, %Y"),
				item.referral.owner.user.username,
				'<a style="margin-right:6px;text-decoration:underline;" href="/edit/%s/">edit</a> <a style="text-decoration:underline;" href="/delete/%s/">delete</a>' % (item.referral.id, item.referral.id),
				"%s %s %s %s %s %s" % (item.referral.date_submitted.year, item.referral.date_submitted.month, item.referral.date_submitted.day, item.referral.date_submitted.hour, item.referral.date_submitted.minute, item.referral.date_submitted.second),
			])
		return json_data

	"""
	def render_column(self, row, column):
		# We want to render custom columns
		if column == 'referral.date_submitted':
			return row.referral.date_submitted.strftime("%B %d, %Y")
		elif column == 'referral.link_title':
			return '<a href="/landing/%s/">%s</a>' % (row.referral.link_title, row.referral.link_title)
		elif column == 'referral.id':
			return '<a style="margin-right:6px" href="/edit/%s/">edit</a> <a href="/delete/%s/">delete</a>' % (row.referral.id, row.referral.id)
		else:
			return super(OrderListJson, self).render_column(row, column)
	"""
	"""
	def filter_queryset(self, qs):
		# use request parameters to filter queryset

		# simple example:
		sSearch = self.request.POST.get('sSearch', None)
		if sSearch:
			qs = qs.filter(name__istartswith=sSearch)

		# more advanced example
		filter_customer = self.request.POST.get('customer', None)

		if filter_customer:
			customer_parts = filter_customer.split(' ')
			qs_params = None
			for part in customer_parts:
				q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
"""

class UserProfileView(JSONResponseMixin, AjaxResponseMixin, UpdateView):
	template_name = 'product/user_profile.html'
	model = Member
	fields = ['quote','bio','image','first_name','last_name']

	def get_success_url(self):
		return '/profile/%s/' % self.request.user.username

	def get_content_type(self):
		return u'application/json'

	def get_form(self, *args, **kwargs):
		return UpdateMemberForm()
	
	def get_object(self, queryset=None):
		return Member.objects.get(user=self.request.user)

	def get_context_data(self, **kwargs):
		context = super(UserProfileView, self).get_context_data(**kwargs)
		return context

	@method_decorator(login_required)
	def get(self, request, username, *args, **kwargs):
		user = request.user
		if user.username != username:
			raise PermissionDenied()

		return render(request, self.template_name, {'member':self.get_object(), 'form':self.get_form(), 'two':'true'})

	@method_decorator(login_required)
	def post_ajax(self, request, *args, **kwargs):
		user = request.user
		if user.username != username:
			raise PermissionDenied()

		form = UpdateMemberForm(request.POST)

		if form.is_valid():
			member = Member.objects.get(user=user)
			member.quote = form.cleaned_data['quote']
			member.bio = form.cleaned_data['bio']
			member.image = form.cleaned_data['image']
			member.user.first_name = form.cleaned_data['first_name']
			member.user.last_name = form.cleaned_data['last_name']
			member.user.save()
			member.save()


class CreateUserAJAX(JSONResponseMixin, AjaxResponseMixin, View):
	content_type = None

	def get_content_type(self):
		return u'application/json'

	def post_ajax(self, request, *args, **kwargs):
		form = CreateUserForm(request.POST)
		if form.is_valid():
			new_user = form.save()
		json_dict = {
			'name':"benny's burritos",
			'location': "New York, NY",
		}
		return HttpResponse('yeahuuuuuhhh')
		#return self.render_json_response(json_dict)

#############################################

class SplashView(TemplateView):
	template_name = 'splash/splash.html'

	def get(self, request, *args, **kwargs):
		form = CreateUserForm()
		user = request.user
		if user.is_authenticated():
			return HttpResponseRedirect('/home/')

		return render(request, self.template_name, {'form':form})

#############################################
"""
class ReferralEditView(UpdateView):
	model = Referral
	template_name = 'product/referral_create.html'
	fields = ['link_title', 'logo_url', 'banner_background_url', 'banner_text', 'font_family']
	success_url = 'home/'
"""

class ReferralDeleteView(View):

	@method_decorator(login_required)
	def get(self, request, referral_id, *args, **kwargs):
		member = Member.objects.get(user=request.user)
		try:
			ref = Referral.objects.get(pk=referral_id)
		except ObjectDoesNotExist:
			raise Http404

		if ref.owner != member:
			raise PermissionDenied
		ref.delete()
		return HttpResponseRedirect('/home/')




class ReferralCreateView(View):
	model = Referral
	template_name = 'product/referral_create.html'
	fields = ['link_title', 'logo_url', 'banner_background_url', 'banner_text', 'font_family']
	success_url = 'home/'

	def get_form(self, *args, **kwargs):
		user = self.request.user
		if user.is_staff:
			return AdminLinkForm()
		return LinkForm()

	@method_decorator(login_required)
	def get(self, request, referral_id=None, *args, **kwargs):
		try:
			member = Member.objects.get(user=request.user)
		except ObjectDoesNotExist:
			raise PermissionDenied
		referral = None
		if referral_id:
			try:
				referral = Referral.objects.get(pk=referral_id)
			except ObjectDoesNotExist:
				raise Http404

			if referral.owner != member:
				raise PermissionDenied

		return render(request, self.template_name, { 'form':self.get_form(), 'member':member, 'object':referral, 'three':'true' })

	@method_decorator(login_required)
	def post(self, request, referral_id=None):
		user = request.user
		if user.is_staff:
			form = AdminLinkForm(request.POST)
		else:
			form = LinkForm(request.POST)

		if form.is_valid():
			member = Member.objects.get(user=user)
			ref = None
			date_submitted = datetime.datetime.now()
			if referral_id:
				try:
					ref = Referral.objects.get(pk=referral_id)
				except ObjectDoesNotExist:
					raise Http404

				if ref.owner != member:
					raise PermissionDenied

				ref.link_title = form.cleaned_data['link_title']
				ref.date_submitted = datetime.datetime.now()
				ref.logo_url = form.cleaned_data['logo_url']
				ref.banner_background_url = form.cleaned_data['banner_background_url']
				ref.banner_text = form.cleaned_data['banner_text']
				ref.font_family = form.cleaned_data['font_family']
				ref.save()

			else:
				ref = Referral.objects.create(
												link_title=form.cleaned_data['link_title'],
												date_submitted=datetime.datetime.now(),
												logo_url=form.cleaned_data['logo_url'],
												banner_background_url=form.cleaned_data['banner_background_url'],
												banner_text=form.cleaned_data['banner_text'],
												font_family=form.cleaned_data['font_family'],
												owner=member,
											)
				ref_stat = ReferralStat.objects.create()
				ref_hist = ReferralHist.objects.create(date=date_submitted, referral=ref, stat=ref_stat)
			return HttpResponseRedirect('/home/')
		else:
			return render(request, self.template_name, { 'form':form })


class HomeView(View):
	template_name = 'product/home.html'

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		member = Member.objects.get(user=request.user)
		return render(request, self.template_name, { 'member':member, 'one':'true' })


class LandingRedirectView(RedirectView):
	permanent = False

	def get_redirect_url(self, title):
		referral = get_object_or_404(Referral, link_title=title)
		ref_hists = ReferralHist.objects.filter(referral=referral)
		hist = ref_hists.order_by('date')[0]
		hist.stat.update_counter()
		hist.stat.save()
		query_params = urllib.urlencode( {'link': title} )
		return '/landing/?'+query_params

class LandingView(DetailView):
	model = Referral
	template_name = 'product/landing.html'
	#queryset = Referral.objects.
	def get(self, request, *args, **kwargs):
		title = request.GET.get('link', '')
		member = Member.objects.get(user=request.user)

		if not title:
			raise Http404
		context = self.get_context_data()
		context['title'] = title
		try:
			ref = Referral.objects.get(link_title=title, owner=member)
		except:
			raise Http404
		context['referral'] = ref
		context['member'] = member
		context['preview'] = 'true'
		return self.render_to_response(context)


class LogoutView(GenericView):
	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		logout(request)
		return redirect('/')


class LoginAuthView(GenericView):
	def post(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated():
			return redirect( request.GET.get('next', '/home') )
		else:
			username = request.POST['username']
			password = request.POST['password']
			
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect( '/home/' )
				
			return redirect( '/home/' )
