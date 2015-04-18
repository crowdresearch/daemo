from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()
from crowdsourcing import views
from crowdsourcing import views as api_views
urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls) ),
    url(r'^login/$', views.Login.as_view()),
    url(r'^register/$', views.Registration.as_view()),
    url(r'^forgot-password/$',views.ForgotPassword.as_view()),
    url(r'^reset-password/(?P<reset_key>\w+)/(?P<enable>[0-1]*)/$',views.reset_password),
    url(r'^registration-successful',views.registration_successful),
    url(r'^terms/$', views.terms),
    url(r'^logout/$', views.Logout.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account-activation/(?P<activation_key>\w+)/$', views.activate_account),
    url(r'^users/(?P<username>.+)/$', views.UserProfile.as_view()),
    #url(r'^hits/$', views.get_hits),
)

urlpatterns += staticfiles_urlpatterns()