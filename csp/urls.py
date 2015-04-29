from crowdsourcing import views
from crowdsourcing import views as api_views
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()
from crowdsourcing import views
from rest_framework.routers import SimpleRouter
router = SimpleRouter()
router.register(r'profile',views.UserProfileViewSet)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls) ),
    url(r'^api/v1/auth/login/$', views.Login.as_view()),
    url(r'^api/v1/auth/register/$', views.Registration.as_view()),
    url(r'^api/v1/auth/forgot-password/$',views.ForgotPassword.as_view()),
    url(r'^api/v1/auth/reset-password/(?P<reset_key>\w+)/(?P<enable>[0-1]*)/$',views.reset_password),
    url(r'^api/v1/auth/registration-successful',views.registration_successful),
    url(r'^api/v1/auth/logout/$', views.Logout.as_view()),
    url(r'^/account-activation/(?P<activation_key>\w+)/$', views.activate_account),
    url(r'^api/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/oauth2-ng/token', views.Oauth2TokenView.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-auth/v1/auth/requesterranking/', views.RequesterRanking.as_view()),
    url(r'', include(router.urls)),
    url('^$', views.home, name='home'),
)

urlpatterns += staticfiles_urlpatterns()
