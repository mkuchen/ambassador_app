from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import resolve, reverse
from django import http
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django_datatables_view.base_datatable_view import BaseDatatableView

from ambassador_app.mixins import *
from braces.views import AjaxResponseMixin, JSONResponseMixin
from cloudinary.forms import cl_init_js_callbacks

from referral_center.decorators import owns_ref
from referral_center.forms import AdminLinkForm, CreateUserForm, LinkForm, UpdateMemberForm
from referral_center.models import Member, Referral, ReferralStat
from vanilla import CreateView, DetailView, FormView, GenericView, RedirectView, TemplateView, UpdateView

import datetime
import json
import sys
import urllib


class LogoutView(GenericView):
	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		logout(request)
		return redirect('/')


class LoginAuthView(GenericView):
	def post(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated():
			return redirect(request.GET.get('next', '/home/'))
		else:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('/home/?slide=true')
			else:
				return redirect('/home/?slide=true')



class UserProfileView(View, AjaxResponseMixin, JSONResponseMixin):
	template_name = 'product/user_profile.html'
	model = Member
	fields = ['quote','bio','profile_image','display_name']

	def get_success_url(self):
		return '/profile/%s/' % self.request.user.username

	def get_form(self, *args, **kwargs):
		return UpdateMemberForm(instance=self.get_object(), data=self.request.POST)
	
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

		context = {
			'form': UpdateMemberForm(instance=self.get_object()),
			'two': True,
			'member': self.get_object()
		}
		return render(request, self.template_name, context)

	@method_decorator(login_required)
	def post(self, request, username, *args, **kwargs):
		user = request.user
		if user.username != username:
			raise PermissionDenied()

		form = UpdateMemberForm(request.POST, request.FILES)
		context = {'form':form, 'two':'true'}
		context['posted'] = form.instance
		if form.is_valid():
			form.save(commit=False)
			mem = self.get_object()
			if form.cleaned_data['profile_image'] is not None:
				mem.profile_image = form.cleaned_data['profile_image']
			mem.display_name = form.cleaned_data['display_name']
			mem.quote = form.cleaned_data['quote']
			mem.bio = form.cleaned_data['bio']
			mem.save()
			context['member'] = mem
		else:
			context['errors'] = form.errors
		return render(request, 'product/user_profile.html', context)




class CreateUserAJAX(JSONResponseMixin, AjaxResponseMixin, View):
	content_type = None

	def get_content_type(self):
		return u'application/json'

	def post_ajax(self, request, *args, **kwargs):
		form = CreateUserForm(request.POST)
		if form.is_valid():
			new_user = form.save()
		else:
			return self.render_json_response({'status': 'error', 'errors': form.errors})

		user = authenticate(username=new_user.username, password=new_user.password)
		if user is not None:
			login(request, user)
			return self.render_json_response({'status': 'ok'})
		else:
			return self.render_json_response({'status': 'error', 'errors': {'login':['there was an error logging you in!']}})

"""
class CreateUser(View):
	def post(self, request, *args, **kwargs):
		form = CreateUserForm(request.POST)
		new_user = None
		if form.is_valid():
			new_user = form.save()
		else:
			return HttpResponseRedirect('/durr/')

		user = authenticate(username=request.POST['username'], password=request.POST['password1'])
		
		if user is not None and user.is_active:
			login(request, user)
			return HttpResponseRedirect('/home/')
		else:
			return HttpResponseRedirect('/hurr/')
"""
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

class ReferralDeleteView(View):
	@owns_ref
	@method_decorator(login_required)
	def get(self, request, referral_id, *args, **kwargs):
		member = Member.objects.get(user=request.user)
		ref = Referral.objects.get(pk=referral_id)
		
		# delete historical tracking data
		stats = ReferralStat.objects.filter(referral=ref)
		for stat in stats:
			stat.delete()
		# delete referral
		ref.delete()
		return HttpResponseRedirect('/home/')


class ReferralPurchaseView(View):
	def get(self, request, referral_id, *args, **kwargs):
		user = request.user
		try:
			referral = Referral.objects.get(pk=referral_id)
		except ObjectDoesNotExist:
			raise Http404
		
		if referral.owner.user != user:
			raise PermissionDenied

		stat = ReferralStat.objects.get(referral=referral, active=True)
		stat.update_purchase()
		redirect_string = '/landing/?link=%s' % referral.link_title

		return HttpResponseRedirect(redirect_string) 


class ReferralCreateView(View):
	model = Referral
	template_name = 'product/referral_create.html'
	fields = ['link_title', 'logo_image', 'banner_image', 'banner_text', 'font_family']
	success_url = 'home/'

	def get_form(self, ref=None, *args, **kwargs):
		user = self.request.user
		if user.is_staff:
			return AdminLinkForm(instance=ref)
		return LinkForm(instance=ref)

	@owns_ref
	@method_decorator(login_required)
	def get(self, request, referral_id=None, *args, **kwargs):		
		if referral_id:
			referral = Referral.objects.get(pk=referral_id)
			context = {
				'form':self.get_form(referral),
				'member':Member.objects.get(user=request.user),
				'object':referral
			}

			if request.GET.get('slide', ''):
				context['slide'] = True

			return render(request, self.template_name, context)

		return render(request, self.template_name, { 'form':self.get_form(), 'member':Member.objects.get(user=request.user), 'three':'true' })

	@owns_ref
	@method_decorator(login_required)
	def post(self, request, referral_id=None, *args, **kwargs):
		ref = None
		member = Member.objects.get(user=request.user)
		if referral_id:
			ref = Referral.objects.get(pk=referral_id)
			
		if user.is_staff:
			form = AdminLinkForm(request.POST, request.FILES)
		else:
			form = LinkForm(request.POST, request.FILES)

		context = {
			'posted': form.instance,
			'form': form,
		}

		if form.is_valid():
			date_submitted = datetime.datetime.now()
			if referral_id:
				ref.link_title = form.cleaned_data['link_title']
				ref.date_submitted = datetime.datetime.now()
				ref.banner_text = form.cleaned_data['banner_text']
				ref.font_family = form.cleaned_data['font_family']
				if form.cleaned_data['logo_image']:
					ref.logo_image = form.cleaned_data['logo_image']
				if form.cleaned_data['banner_image']:
					ref.banner_image = form.cleaned_data['banner_image']
				ref.save()
			else:
				ref = Referral.objects.create(
					link_title=form.cleaned_data['link_title'],
					date_submitted=datetime.datetime.now(),
					banner_text=form.cleaned_data['banner_text'],
					font_family=form.cleaned_data['font_family'],
					owner=member,
				)

				ReferralStat.objects.create(
					referral=ref,
					latest=True,
					active=False,
					date_recorded=datetime.datetime.now()
				)

				ReferralStat.objects.create(
					referral=ref,
					latest=False,
					active=True
				)
				if form.cleaned_data['banner_image']:
					ref.banner_image=form.cleaned_data['banner_image']
				if form.cleaned_data['logo_image']:
					ref.logo_image=form.cleaned_data['logo_image']
				ref.save()

			return HttpResponseRedirect('/home/')
		else:
			context['errors'] = form.errors
			context['form'] = form
			if ref:
				context['object'] = ref
			if member:
				context['member'] = member
			return render(request, self.template_name, context)


class HomeView(View):
	template_name = 'product/home.html'

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		member = Member.objects.get(user=request.user)
		context = {
					'member':member,
					'one':'true'
				}
		if request.GET.get('slide', ''):
			context['slide'] = True
		return render(request, self.template_name, context)


class LandingRedirectView(RedirectView):
	permanent = False

	def get_redirect_url(self, title):
		referral = get_object_or_404(Referral, link_title=title)
		stat = ReferralStat.objects.get(referral=referral, active=True)
		stat.update_counter()
		query_params = urllib.urlencode( {'link': title} )
		return '/landing/?'+query_params

class LandingPreviewView(DetailView):
	model = Referral
	template_name = 'product/landing.html'

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		title = request.GET.get('link', '')
		if not title:
			raise Http404
		
		member = get_object_or_404(Member, user=request.user)
		ref = get_object_or_404(Referral, link_title=title)

		if ref.owner != member:
			raise PermissionDenied

		context = {
			'title' : title,
			'referral' : ref,
			'member' : member,
			'preview' : 'true',
		}
		return self.render_to_response(context)

class LandingView(DetailView):
	model = Referral
	template_name = 'product/landing.html'

	def get(self, request, *args, **kwargs):
		title = request.GET.get('link', '')
		
		if not title:
			raise Http404
		
		ref = get_object_or_404(Referral, link_title=title)

		context = {
			'title': title,
			'referral': ref,
		}
		return self.render_to_response(context)


class OrderListJson(BaseDatatableView):
	# The model we're going to show
	model = ReferralStat

	# define the columns that will be returned
	columns = [
		'referral.link_title', 'num_clicks', 'num_purchases',
		'referral.date_submitted','referral.owner.user.username', 'referral.id',
		'referral.date_submitted'
	]

	# define column names that will be used in sorting
	# order is important and should be same as order of columns
	# displayed by datatables. For non sortable columns use empty
	# value like ''
	order_columns = ['referral.link_title', 'num_clicks',
						'num_purchases', 'referral.date_submitted', '', '']

	max_display_length = 500

	def get_initial_queryset(self):
		#return ReferralStat.objects.all()
		return ReferralStat.objects.filter(active=True).filter(referral__owner__user=self.request.user)

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			json_data.append([
				item.referral.link_title,
				item.num_clicks,
				item.num_purchases,
				item.referral.date_submitted.strftime("%B %d, %Y"),
				item.referral.id,
				"%s %s %s %s %s %s" % (	
					item.referral.date_submitted.year,
					item.referral.date_submitted.month,
					item.referral.date_submitted.day,
					item.referral.date_submitted.hour,
					item.referral.date_submitted.minute,
					item.referral.date_submitted.second,
				),
			])
		return json_data



class ChartDataJson(JSONResponseMixin, AjaxResponseMixin, View):
	content_type = None

	def get_content_type(self):
		return u'application/json'

	@owns_ref
	def get_ajax(self, request, referral_id, *args, **kwargs):
		try:
			ref = Referral.objects.get(pk=referral_id)
		except ObjectDoesNotExist:
			raise Http404
	
		
		stats = ReferralStat.objects.filter(referral=ref).filter(active=False)
		clicks = [ (
			(
				stat.date_recorded.year, \
				stat.date_recorded.month-1, \
				stat.date_recorded.day, \
				stat.date_recorded.hour, \
				stat.date_recorded.minute, \
				stat.date_recorded.second, \
				stat.date_recorded.microsecond,
			),
			stat.num_clicks,
		) for stat in stats ]

		purchases = [ (
			(
				stat.date_recorded.year, \
				stat.date_recorded.month-1, \
				stat.date_recorded.day, \
				stat.date_recorded.hour, \
				stat.date_recorded.minute, \
				stat.date_recorded.second, \
				stat.date_recorded.microsecond,
			),
			stat.num_purchases,
		) for stat in stats ]

		click_thrus = [ (
			(
				stat.date_recorded.year, \
				stat.date_recorded.month-1, \
				stat.date_recorded.day, \
				stat.date_recorded.hour, \
				stat.date_recorded.minute, \
				stat.date_recorded.second, \
				stat.date_recorded.microsecond,
			),
			(stat.num_purchases / stat.num_clicks),
		) for stat in stats ]
		json_dict = { 'clicks': clicks, 'purchases': purchases, 'click-thrus': click_thrus}
		return self.render_json_response(json_dict)

