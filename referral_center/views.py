from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from referral_center.forms import AdminLinkForm, LinkForm
from referral_center.models import Referral
from vanilla import CreateView, FormView, TemplateView, GenericView, DetailView
from ambassador_app.mixins import *

import datetime
import urllib

class SplashView(GenericView):
	template_name = 'login.html'
	def get(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated():
			return redirect('/home/')
		else:
			return render(request, self.template_name)


class HomeView(CreateView):
	template_name = 'home.html'
	model = Referral
	success_url = 'home/'
	fields = ['link_title', 'link_url']

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
			url = form.cleaned_data['link_url']
			user = request.user
			date_submitted = datetime.datetime.now()
			ref = Referral.objects.create(link_title=title, link_url=url, owner=user, date_submitted=date_submitted)
			return HttpResponseRedirect('/home/')
		else:
			return HttpResponseRedirect('/home/')

class TitleView(DetailView):
	model = Referral
	#template_name = 'landing_base.html'
	#queryset = Referral.objects.
	def get(self, request, *args, **kwargs):
		try:
			link_dict = { 'link' : kwargs['title'] }
			title = urllib.urlencode( link_dict )
		except KeyError:
			raise Http404
		#context = self.get_context_data()
		#return self.render_to_response(context)
		return redirect('/landing/?', title)

class LandingView(DetailView):
	model = Referral
	template_name = 'landing_base.html'

	def get(self, request, *args, **kwargs):
		title = kwargs['link']
		context = self.get_context_data()
		context['title'] = title
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