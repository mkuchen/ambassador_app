from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django import http
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from referral_center.forms import AdminLinkForm, LinkForm, CreateUserForm
from referral_center.models import Referral, ReferralStat, ReferralHist, Member
from vanilla import CreateView, FormView, TemplateView, GenericView, DetailView, RedirectView, UpdateView
from ambassador_app.mixins import *
from braces.views import AjaxResponseMixin, JSONResponseMixin

import datetime
import urllib
import json

class OrderListJson(BaseDatatableView):
	# The model we're going to show
	model = ReferralHist

	# define the columns that will be returned
	columns = ['referral.link_title', 'stat.num_clicks', 'referral.date_submitted', 'referral.owner.user.username']

	# define column names that will be used in sorting
	# order is important and should be same as order of columns
	# displayed by datatables. For non sortable columns use empty
	# value like ''
	order_columns = ['referral.link_title', 'stat.num_clicks', 'referral.date_submitted', '']

	# set max limit of records returned, this is used to protect our site if someone tries to attack our site
	# and make it return huge amount of data
	max_display_length = 500


	def render_column(self, row, column):
		# We want to render user as a custom column
		if column == 'referral.date_submitted':
			return row.referral.date_submitted.strftime("%B %d, %Y")
		elif column == 'referral.link_title':
			return '<a href="/landing/%s/">%s</a>' % (row.referral.link_title, row.referral.link_title)
		else:
			return super(OrderListJson, self).render_column(row, column)

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


class UserProfileView(DetailView):
	template_name = 'product/user_profile.html'
	model = Member
	
	def get_object(self, queryset=None):
		return Member.objects.get(user=self.request.user)

	def get_context_data(self, **kwargs):
		context = super(ProfileView, self).get_context_data(**kwargs)
		return context

	@method_decorator(login_required)
	def get(self, request, username, *args, **kwargs):
		user = request.user
		if user.username != username:
			raise PermissionDenied()

		return render(request, self.template_name, {'object':self.get_object()})

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
		return render(request, self.template_name, {'form':form})

###################################################


class HomeView(CreateView):
	template_name = 'product/home.html'
	model = Referral
	success_url = 'home/'
	fields = ['link_title']

	def get_form(self, *args, **kwargs):
		user = self.request.user
		if user.is_staff:
			return AdminLinkForm()
		return LinkForm()

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, { 'form':self.get_form() })

	@method_decorator(login_required)
	def post(self, request):
		user = request.user
		if user.is_staff:
			form = AdminLinkForm(request.POST)
		else:
			form = LinkForm(request.POST)

		if form.is_valid():
			title = form.cleaned_data['link_title']
			user = request.user
			member = Member.objects.get(user=user)
			date_submitted = datetime.datetime.now()
			ref = Referral.objects.create(link_title=title, owner=member, date_submitted=date_submitted)
			ref_stat = ReferralStat.objects.create()
			ref_hist = ReferralHist.objects.create(date=date_submitted, referral=ref, stat=ref_stat)
			return HttpResponseRedirect('/home/')
		else:
			return render(request, self.template_name, { 'form':form })

class LandingRedirectView(RedirectView):
	permanent = False

	def get_redirect_url(self, title):
		referral = get_object_or_404(Referral, link_title=title)
		referral.update_counter()
		referral.save()
		query_params = urllib.urlencode( {'link': title} )
		return '/landing/?'+query_params

class LandingView(DetailView):
	model = Referral
	template_name = 'product/landing_base.html'
	#queryset = Referral.objects.
	def get(self, request, *args, **kwargs):
		title = request.GET.get('link', '')
		if not title:
			raise Http404
		context = self.get_context_data()
		context['title'] = title
		try:
			ref = Referral.objects.get(link_title=title)
		except:
			raise Http404
		context['referral'] = ref
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
