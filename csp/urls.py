from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from crowdsourcing import views
from crowdsourcing.viewsets.project import *
from crowdsourcing.viewsets.user import UserViewSet, UserProfileViewSet, UserPreferencesViewSet
from crowdsourcing.viewsets.requester import RequesterRankingViewSet, RequesterViewSet, QualificationViewSet
from crowdsourcing.viewsets.worker import *
from crowdsourcing.viewsets.task import TaskViewSet, CurrencyViewSet, TaskWorkerResultViewSet, TaskWorkerViewSet
from crowdsourcing.viewsets.template import TemplateViewSet, TemplateItemViewSet,TemplateItemPropertiesViewSet
from crowdsourcing.viewsets.drive import *
from crowdsourcing.viewsets.google_drive import GoogleDriveOauth, GoogleDriveViewSet
from crowdsourcing.viewsets.message import ConversationViewSet, MessageViewSet
from crowdsourcing.viewsets.csvmanager import CSVManagerViewSet


from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash=True)
router.register(r'api/profile',UserProfileViewSet)
router.register(r'api/user', UserViewSet)
router.register(r'api/preferences', UserPreferencesViewSet)
router.register(r'api/requester-ranking', RequesterRankingViewSet)
router.register(r'api/requester', RequesterViewSet)
router.register(r'api/project', ProjectViewSet)
router.register(r'api/category', CategoryViewSet)
router.register(r'api/module', ModuleViewSet,base_name = 'module')
router.register(r'api/project-requester', ProjectRequesterViewSet)
router.register(r'api/worker-skill', WorkerSkillViewSet)
router.register(r'api/worker', WorkerViewSet)
router.register(r'api/skill', SkillViewSet)
router.register(r'api/task', TaskViewSet)
router.register(r'api/task-worker', TaskWorkerViewSet)
router.register(r'api/task-worker-result', TaskWorkerResultViewSet)
router.register(r'api/worker-module-application', WorkerModuleApplicationViewSet)
router.register(r'api/qualification', QualificationViewSet)
router.register(r'api/currency', CurrencyViewSet)
router.register(r'api/template', TemplateViewSet)
router.register(r'api/template-item', TemplateItemViewSet)
router.register(r'api/template-item-properties', TemplateItemPropertiesViewSet)
router.register(r'api/drive-account', AccountModelViewSet)
router.register(r'api/bookmark-project', BookmarkedProjectsViewSet)
router.register(r'api/conversation', ConversationViewSet)
router.register(r'api/message', MessageViewSet)
#router.register(r'api/google-drive', GoogleDriveOauth)

urlpatterns = patterns('',
  url(r'^api/v1/auth/forgot-password/$',views.ForgotPassword.as_view()),
  url(r'^api/v1/auth/reset-password/(?P<reset_key>\w+)/(?P<enable>[0-1]*)/$',views.reset_password),
  url(r'^api/v1/auth/registration-successful',views.registration_successful),
  url(r'^api/auth/login/$', views.Login.as_view()),
  url(r'^api/auth/logout/$', views.Logout.as_view()),
  url(r'^/account-activation/(?P<activation_key>\w+)/$', views.activate_account),
  url(r'^api/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
  url(r'^api/oauth2-ng/token', views.Oauth2TokenView.as_view()),
  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
  url(r'^api/google-drive/init', GoogleDriveOauth.as_view({'post': 'auth_init'})),
  url(r'^api/google-drive/finish', GoogleDriveOauth.as_view({'post': 'auth_end'})),
  url(r'^api/google-drive/list-files', GoogleDriveViewSet.as_view({'get': 'query'})),
  url(r'^api/csvmanager/get-metadata-and-save', CSVManagerViewSet.as_view({'post': 'get_metadata_and_save'})),
  url(r'^api/csvmanager/download-results', CSVManagerViewSet.as_view({'get': 'download_results'})),
  url(r'', include(router.urls)),
  url('^.*$', views.home, name='home'),
)

urlpatterns += staticfiles_urlpatterns()
