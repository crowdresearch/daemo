from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from crowdsourcing import views
from crowdsourcing.viewsets.project import *
from crowdsourcing.viewsets.user import UserViewSet, UserProfileViewSet, UserPreferencesViewSet
from crowdsourcing.viewsets.requester import RequesterRankingViewSet, RequesterViewSet

from crowdsourcing.viewsets.worker import SkillViewSet, WorkerSkillViewSet, WorkerViewSet, \
    WorkerModuleApplicationViewSet, TaskWorkerResultViewSet, CurrencyViewSet, \
    TaskWorkerViewSet

from crowdsourcing.viewsets.task import QualificationViewSet, TaskViewSet

from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=True)
router.register(r'profile', UserProfileViewSet)
router.register(r'user', UserViewSet)
router.register(r'preferences', UserPreferencesViewSet)
router.register(r'requester-ranking', RequesterRankingViewSet)
router.register(r'requester', RequesterViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'module', ModuleViewSet)
router.register(r'project-requester', ProjectRequesterViewSet)
router.register(r'worker-skill', WorkerSkillViewSet)
router.register(r'worker', WorkerViewSet)
router.register(r'skill', SkillViewSet)
router.register(r'task', TaskViewSet)
router.register(r'task-worker', TaskWorkerViewSet)
router.register(r'worker-module-application', WorkerModuleApplicationViewSet)
router.register(r'qualification', QualificationViewSet)
router.register(r'currency', CurrencyViewSet)

auth_urls = patterns('',
                     url(r'^auth/forgot-password/$', views.ForgotPassword.as_view()),
                     url(r'^auth/reset-password/(?P<reset_key>\w+)/(?P<enable>[0-1]*)/$',
                         views.reset_password),
                     url(r'^auth/registration-successful/$', views.registration_successful),
                     url(r'^auth/logout/$', views.Logout.as_view()),
)

urlpatterns = patterns('',

                       url(r'^account-activation/(?P<activation_key>\w+)/$', views.activate_account),
                       url(r'^api/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
                       url(r'^api/oauth2-ng/token', views.Oauth2TokenView.as_view()),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       url(r'^api/v1/', include(router.urls + auth_urls)),

                       url(r'^$', views.home, name='home'),
)

urlpatterns += staticfiles_urlpatterns()
