from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required, permission_required
from referral_center.views import *
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', SplashView.as_view(), name='base'),
    url(r'^new-account/$', CreateUser.as_view(), name='create_user'),
    url(r'^profile/(?P<username>[\w|\W]+)/$', UserProfileView.as_view(), name='update_user'),
    # url(r'^ambassador_app/', include('ambassador_app.foo.urls')),
    url(r'^create/$', ReferralCreateView.as_view(), name='create_referral'),
    url(r'^edit/(?P<referral_id>[\w|\W]+)/$', ReferralCreateView.as_view(), name='edit_referral'),
    url(r'^delete/(?P<referral_id>[\w|\W]+)/$', ReferralDeleteView.as_view(), name='delete_referral'),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^landing/(?P<title>[\w|\W]+)/$', LandingRedirectView.as_view()),
    url(r'^landing/$', LandingView.as_view(), name='main_landing'),
    url(r'^datatables/all-refs/$', login_required(OrderListJson.as_view()), name='order_list_json'),
    url(r'^splash/$', SplashView.as_view()),
    url(r'^login-auth/$', LoginAuthView.as_view(), name='auth'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    ###########################
    #url(r'^admin/doc/$', include('django.contrib.admindocs.urls')),
    #url(r'^admin/$', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
