from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django_datatables_view.base_datatable_view import BaseDatatableView
from referral_center.forms import AdminLinkForm, LinkForm
from referral_center.models import Referral
from vanilla import CreateView, FormView, TemplateView, GenericView, DetailView, RedirectView
from ambassador_app.mixins import *

import datetime
import urllib

class OrderListJson(BaseDatatableView):
	# The model we're going to show
	model = Referral

	# define the columns that will be returned
	columns = ['link_title', 'clicks', 'date_submitted', 'owner.username']

	# define column names that will be used in sorting
	# order is important and should be same as order of columns
	# displayed by datatables. For non sortable columns use empty
	# value like ''
	order_columns = ['link_title', 'clicks', 'date_submitted', '']

	# set max limit of records returned, this is used to protect our site if someone tries to attack our site
	# and make it return huge amount of data
	max_display_length = 500


	def render_column(self, row, column):
		# We want to render user as a custom column
		if column == 'date_submitted':
			return row.date_submitted.strftime("%B %d, %Y")
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

class SplashView(GenericView):
	template_name = 'home.html'
	def get(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated():
			#return redirect('/home/')
			return render(request, self.template_name, {'authenticated':'True'})
		else:
			return render(request, self.template_name, {})


class HomeView(CreateView):
	template_name = 'home.html'
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
		all_referrals = Referral.objects.all()
		return render(request, self.template_name, { 'refs':all_referrals, 'form':self.get_form() })

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
			date_submitted = datetime.datetime.now()
			ref = Referral.objects.create(link_title=title, owner=user, date_submitted=date_submitted)
			return HttpResponseRedirect('/home/')
		else:
			all_referrals = Referral.objects.all()
			return render(request, self.template_name, {'refs':all_referrals, 'form':form})
			#return HttpResponseRedirect('/home/', form=form)

class LandingRedirectView(RedirectView):
	permanent = False

	def get_redirect_url(self, title):
		referral = get_object_or_404(Referral, link_title=title)
		referral.update_counter()
		query_params = urllib.urlencode( {'link': title} )
		return '/landing/?'+query_params

class LandingView(DetailView):
	model = Referral
	template_name = 'landing_base.html'
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
	template_name = 'logged_out.html'

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		logout(request)
		return render(request, self.template_name)

class LoginUserView(FormView):
	template_name = 'login.html'

	def get(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated():
			return redirect( request.GET.get('next', '/home') )
		else:
			return render(request, self.template_name)

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
				return redirect( '/welcome/', next=request.GET.get('next', '/home') )
			else:
				return redirect( '/incorrect-login/' )


class IncorrectLoginView(GenericView):
	template_name = 'incorrect_login.html'

	def get(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated():
			return redirect('/home/')
		else:
			return render(request, self.template_name)

class WelcomeView(GenericView):
	template_name = 'welcome.html'

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		user = self.request.user
		name = "%s %s" % (user.first_name, user.last_name)
		return render(request, 'welcome.html', {'name': name, 'next':request.GET.get('next', '/home')})

"""
class AuthLoginView(View):
	model = User
	def get_form(self, data=None, files=None, **kwargs):
"""