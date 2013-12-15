from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required
from referral_center.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', SplashView.as_view()),
    # url(r'^ambassador_app/', include('ambassador_app.foo.urls')),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^landing/(?P<title>[\w|\W]+)/$', LandingRedirectView.as_view()),
    url(r'^landing/$', LandingView.as_view(), name='main_landing'),
    url(r'^datatables/all-refs/$', login_required(OrderListJson.as_view()), name='order_list_json'),
    url(r'^incorrect-login/$', IncorrectLoginView.as_view()),
    url(r'^splash/$', SplashView.as_view()),
    url(r'^accounts/login/$', LoginUserView.as_view(), name='login'),
    url(r'^login-auth/$', LoginAuthView.as_view(), name='auth'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    ###########################
    url(r'^admin/doc/$', include('django.contrib.admindocs.urls')),
    url(r'^admin/$', include(admin.site.urls)),
)
