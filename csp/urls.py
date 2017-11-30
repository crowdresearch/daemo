from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from rest_framework.routers import SimpleRouter

from crowdsourcing import views
from crowdsourcing.viewsets.file import FileViewSet
from crowdsourcing.viewsets.message import ConversationViewSet, MessageViewSet, RedisMessageViewSet, \
    ConversationRecipientViewSet
from crowdsourcing.viewsets.payment import ChargeViewSet, TransferViewSet
from crowdsourcing.viewsets.project import *
from crowdsourcing.viewsets.qualification import QualificationViewSet, RequesterACGViewSet, WorkerACEViewSet, \
    QualificationItemViewSet
from crowdsourcing.viewsets.rating import WorkerRequesterRatingViewset, RatingViewset
from crowdsourcing.viewsets.task import TaskViewSet, TaskWorkerResultViewSet, TaskWorkerViewSet, \
    ExternalSubmit, ReturnFeedbackViewSet
from crowdsourcing.viewsets.template import TemplateViewSet, TemplateItemViewSet, TemplateItemPropertiesViewSet
from crowdsourcing.viewsets.user import UserViewSet, UserProfileViewSet, UserPreferencesViewSet, CountryViewSet, \
    CityViewSet
from mturk import views as mturk_views
from mturk.viewsets import MTurkAssignmentViewSet, MTurkConfig, MTurkAccountViewSet

router = SimpleRouter(trailing_slash=True)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'assignments', TaskWorkerViewSet)
router.register(r'templates', TemplateViewSet)
router.register(r'template-items', TemplateItemViewSet)

router.register(r'profile', UserProfileViewSet)
router.register(r'user', UserViewSet)
router.register(r'preferences', UserPreferencesViewSet)
router.register(r'worker-requester-rating', WorkerRequesterRatingViewset)
router.register(r'rating', RatingViewset)

router.register(r'country', CountryViewSet)
router.register(r'city', CityViewSet)

router.register(r'task-worker', TaskWorkerViewSet)
router.register(r'task-worker-result', TaskWorkerResultViewSet)
router.register(r'template', TemplateViewSet)
router.register(r'template-item', TemplateItemViewSet)
router.register(r'template-item-properties', TemplateItemPropertiesViewSet)
router.register(r'return-feedback', ReturnFeedbackViewSet)
router.register(r'conversation', ConversationViewSet)
router.register(r'conversation-recipients', ConversationRecipientViewSet)
router.register(r'message', MessageViewSet)
router.register(r'inbox', RedisMessageViewSet, base_name='redis-message')
router.register(r'file', FileViewSet)
router.register(r'qualification', QualificationViewSet)
router.register(r'requester-access-group', RequesterACGViewSet)
router.register(r'worker-access-entry', WorkerACEViewSet)
router.register(r'qualification-item', QualificationItemViewSet)
router.register(r'charges', ChargeViewSet)
router.register(r'transfers', TransferViewSet)

mturk_router = SimpleRouter(trailing_slash=False)
mturk_router.register(r'mturk', MTurkAssignmentViewSet)
mturk_router.register(r'mturk-account', MTurkAccountViewSet)

urlpatterns = [
    url(r'^api/auth/login/$', views.Login.as_view()),
    url(r'^api/auth/logout/$', views.Logout.as_view()),
    url(r'^api/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/oauth2-ng/token', views.Oauth2TokenView.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/done/$', csrf_exempt(ExternalSubmit.as_view())),
    url(r'^v1/done/$', csrf_exempt(ExternalSubmit.as_view())),
    url(r'^api/external-tasks/$', csrf_exempt(ExternalSubmit.as_view())),
    url(r'^api/', include(router.urls)),
    url(r'^v1/', include(router.urls)),
    url(r'^mturk/task', mturk_views.mturk_index),
    url(r'^api/', include(mturk_router.urls)),
    url(r'^api/mturk/url', MTurkConfig.as_view({'get': 'get_mturk_url'})),

    url(r'^advice', RedirectView.as_view(url='https://docs.google.com/forms/d/e/1FAIpQLScB5yz_'
                                             '2gdJOjSDu76gqDrMpUyiczQt-MTgtii4QLhuoP3YMA/viewform'),
        name='advice'),

    url(r'^forum', RedirectView.as_view(url=settings.DISCOURSE_BASE_URL), name='forum'),
    url(r'^discourse/sso$', views.sso),

    url('^.*$', views.home, name='home')
]

urlpatterns += staticfiles_urlpatterns()
