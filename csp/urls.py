from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from crowdsourcing import views
from mturk import views as mturk_views
from crowdsourcing.viewsets.project import *
from crowdsourcing.viewsets.user import UserViewSet, UserProfileViewSet, UserPreferencesViewSet
from crowdsourcing.viewsets.requester import RequesterViewSet, QualificationViewSet
from crowdsourcing.viewsets.rating import WorkerRequesterRatingViewset, RatingViewset
from crowdsourcing.viewsets.worker import *
from crowdsourcing.viewsets.task import TaskViewSet, TaskWorkerResultViewSet, TaskWorkerViewSet, \
    ExternalSubmit
from crowdsourcing.viewsets.template import TemplateViewSet, TemplateItemViewSet, TemplateItemPropertiesViewSet
from crowdsourcing.viewsets.drive import *
from crowdsourcing.viewsets.google_drive import GoogleDriveOauth, GoogleDriveViewSet
from crowdsourcing.viewsets.message import ConversationViewSet, MessageViewSet
from crowdsourcing.viewsets.file import FileViewSet
from crowdsourcing.viewsets.payment import PayPalFlowViewSet, FinancialAccountViewSet
from rest_framework.routers import SimpleRouter
from mturk.viewsets import MTurkAssignmentViewSet, MTurkConfig

router = SimpleRouter(trailing_slash=True)
router.register(r'api/profile', UserProfileViewSet)
router.register(r'api/user', UserViewSet)
router.register(r'api/preferences', UserPreferencesViewSet)
router.register(r'api/worker-requester-rating', WorkerRequesterRatingViewset)
router.register(r'api/rating', RatingViewset)
router.register(r'api/requester', RequesterViewSet)
router.register(r'api/project', ProjectViewSet)
router.register(r'api/category', CategoryViewSet)

router.register(r'api/worker-skill', WorkerSkillViewSet)
router.register(r'api/worker', WorkerViewSet)
router.register(r'api/skill', SkillViewSet)
router.register(r'api/task', TaskViewSet)
router.register(r'api/task-worker', TaskWorkerViewSet)
router.register(r'api/task-worker-result', TaskWorkerResultViewSet)
router.register(r'api/qualification', QualificationViewSet)
router.register(r'api/template', TemplateViewSet)
router.register(r'api/template-item', TemplateItemViewSet)
router.register(r'api/template-item-properties', TemplateItemPropertiesViewSet)
router.register(r'api/drive-account', AccountModelViewSet)
router.register(r'api/conversation', ConversationViewSet)
router.register(r'api/message', MessageViewSet)
# router.register(r'api/google-drive', GoogleDriveOauth)
router.register(r'api/payment-paypal', PayPalFlowViewSet)
router.register(r'api/financial-accounts', FinancialAccountViewSet)
router.register(r'^api/file', FileViewSet)

mturk_router = SimpleRouter(trailing_slash=False)
mturk_router.register(r'^api/mturk', MTurkAssignmentViewSet)

urlpatterns = patterns('',
                       url(r'^api/v1/auth/registration-successful', views.registration_successful),
                       url(r'^api/auth/login/$', views.Login.as_view()),
                       url(r'^api/auth/logout/$', views.Logout.as_view()),
                       url(r'^api/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
                       url(r'^api/oauth2-ng/token', views.Oauth2TokenView.as_view()),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^api/google-drive/init', GoogleDriveOauth.as_view({'post': 'auth_init'})),
                       url(r'^api/google-drive/finish', GoogleDriveOauth.as_view({'post': 'auth_end'})),
                       url(r'^api/google-drive/list-files', GoogleDriveViewSet.as_view({'get': 'query'})),
                       url(r'^api/done/$', ExternalSubmit.as_view()),
                       url(r'', include(router.urls)),

                       url(r'^mturk/task', mturk_views.mturk_index),
                       url(r'', include(mturk_router.urls)),
                       url(r'^api/mturk/url', MTurkConfig.as_view({'get': 'get_mturk_url'})),

                       url('^.*$', views.home, name='home'),
                       )

urlpatterns += staticfiles_urlpatterns()
