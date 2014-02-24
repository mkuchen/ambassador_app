import functools
from models import Referral, Member
from django.contrib.auth.models import User

from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator

def owns_ref(method):
	@functools.wraps(method)
	def wrapper(self, request, referral_id=None, *args, **kwargs):
		mem = None

		if referral_id is None:
			return method(self, request, None, args, kwargs)

		if request.user.is_authenticated():
			try:
				mem = Member.objects.get(user=request.user)
			except ObjectDoesNotExist:
				raise Http404
		else:
			raise PermissionDenied

		ref = get_object_or_404(Referral, pk=referral_id)
		if ref.owner != mem:
			raise PermissionDenied
		return method(self, request, referral_id, args, kwargs)
	return wrapper

def require_AJAX(view):
    def ajaxOnly(function):
        def wrap(request, *args, **kwargs):
            if not request.is_ajax():
                return HttpResponseForbidden()
            return function(request, *args, **kwargs)
 
        return wrap
 
    view.dispatch = method_decorator(ajaxOnly)(view.dispatch)
    return view

"""
def check_slide(method):
	@functools.wraps(method)
	def wrapper(self, request, referral_id=None, *args, **kwargs):
		if request.GET.get('slide', ''):
"""