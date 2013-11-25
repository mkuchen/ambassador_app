from django import forms

class AdminLinkForm(forms.Form):
	link_title = forms.SlugField(max_length=500)

class LinkForm(forms.Form):
	link_title = forms.SlugField(max_length=500)
