from rest_framework import permissions
from csp import settings
from rest_framework.exceptions import PermissionDenied
from crowdsourcing.models import RegistrationWhitelist


class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.is_worker


class IsRequester(permissions.BasePermission):
    def has_object_permission(self, request, view, object):
        return request.user.profile.is_requester


class CanCreateAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        user_email = request.data.get('email')
        users = RegistrationWhitelist.objects.filter(email=user_email).count()
        if view.action == 'create' and not (request.user.is_staff or settings.REGISTRATION_ALLOWED) and users == 0:
            raise PermissionDenied(detail='We are currently in closed beta. '
                                          'If you\'d like an account, email daemo@cs.stanford.edu '
                                          'with a short description of what you\'d like to use Daemo for.')
        return True
