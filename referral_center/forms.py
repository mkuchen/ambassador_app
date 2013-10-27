from django import forms

class AdminLinkForm(forms.Form):
	link_title = forms.CharField(max_length=500)
	link_url = forms.CharField(max_length=500)

class LinkForm(forms.Form):
	link_title = forms.CharField(max_length=500)
	link_url = forms.CharField(max_length=500)