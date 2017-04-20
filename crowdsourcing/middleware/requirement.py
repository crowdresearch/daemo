from django.http import JsonResponse
from crowdsourcing.utils import get_worker_cache


class RequirementMiddleware():
    def __init__(self, get_response=None):
        self.get_response = get_response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api/auth') or request.path.startswith('/api/profile/'):
            return None
        if not request.user.is_anonymous() and request.path.startswith('/api'):
            worker_cache = get_worker_cache(request.user.id)
            if not (int(worker_cache.get('is_worker', 0)) or int(worker_cache.get('is_requester', 0))):
                return JsonResponse(data={'type': 'error', 'message': 'MISSING_USER_INFORMATION', 'code': 'D-000'},
                                    status=400)
