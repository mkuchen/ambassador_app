from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required
from referral_center.views import ReferralCreate
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ambassador_app.views.home', name='home'),
    # url(r'^ambassador_app/', include('ambassador_app.foo.urls')),
    url(r'^$', ReferralCreate.as_view(template_name="home.html")),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
