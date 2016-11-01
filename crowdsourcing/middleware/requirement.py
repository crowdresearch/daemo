from django.http import JsonResponse
from crowdsourcing.utils import get_worker_cache


class RequirementMiddleware():
    def __init__(self, get_response=None):
        self.get_response = get_response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api/auth') or request.path.startswith('/api/profile/stripe'):
            return None
        return None
        if not request.user.is_anonymous() and request.path.startswith('/api'):
            worker_cache = get_worker_cache(request.user.id)
            if not (worker_cache.get('is_worker', False) or worker_cache.get('is_requester', False)):
                return JsonResponse(data={'error': 'MISSING_USER_INFORMATION', 'code': 'D-000'}, status=400)
