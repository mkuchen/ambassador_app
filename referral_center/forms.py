from django import forms
from django.contrib.auth.models import User
from referral_center.models import Member

class AdminLinkForm(forms.Form):
	link_title = forms.SlugField(max_length=500)
	logo_url = forms.URLField(max_length=1000)
	banner_background_url = forms.URLField(max_length=1000)
	banner_text = forms.CharField(max_length=1000)
	font_family = forms.CharField(max_length=500)

class LinkForm(forms.Form):
	link_title = forms.SlugField(max_length=500)
	logo_url = forms.URLField(max_length=1000)
	banner_background_url = forms.URLField(max_length=1000)
	banner_text = forms.CharField(max_length=1000)
	font_family = forms.CharField(max_length=500)

class UpdateMemberForm(forms.Form):
	quote = forms.CharField(max_length=300)
	bio = forms.CharField(max_length=2000)
	#image = forms.CharField(max_length=1000)
	image = forms.FileField(
		label='Select a file',
		help_text='max. 42 megabytes'
	)
	first_name = forms.CharField(max_length=100)
	last_name = forms.CharField(max_length=100)

class CreateUserForm(forms.Form):
	username = forms.CharField(required=True)
	first_name = forms.CharField(required=True)
	last_name = forms.CharField(required=True)
	password1 = forms.CharField(max_length=30, widget=forms.PasswordInput())
	password2 = forms.CharField(max_length=30, widget=forms.PasswordInput())
	email = forms.EmailField(required=True)

	def clean_username(self):
		try:
			User.objects.get(username=self.cleaned_data['username']) #get user from user model
		except User.DoesNotExist :
			return self.cleaned_data['username']

		raise forms.ValidationError("this username isn't available")

	def clean(self):
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError("passwords dont match each other")
		
		return self.cleaned_data
	
	def save(self):
		new_user = User.objects.create_user(username=self.clean_username(),
											email=self.cleaned_data['email'],
											password=self.cleaned_data['password1'])
		new_user.first_name = self.cleaned_data['first_name']
		new_user.last_name = self.cleaned_data['last_name']
		new_user.save()
		new_member = Member.objects.create(user=new_user, quote="", bio="")
		return new_user

"""
class AdminUserProfileForm(forms.Form):
	# fields

class UserProfileForm(forms.Form):
	# more fields...
"""