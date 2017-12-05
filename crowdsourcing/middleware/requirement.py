from django.http import JsonResponse

from crowdsourcing.utils import get_worker_cache


class RequirementMiddleware():
    def __init__(self, get_response=None):
        self.get_response = get_response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        allowed_paths = ['/api/auth', '/api/profile/', '/api/user/is-whitelisted']
        for path in allowed_paths:
            if request.path.startswith(path):
                return None
        if not request.user.is_anonymous() and (request.path.startswith('/api') or request.path.startswith('/v1')):
            worker_cache = get_worker_cache(request.user.id)
            if not (int(worker_cache.get('is_worker', 0)) or int(worker_cache.get('is_requester', 0))):
                return JsonResponse(data={'type': 'error', 'message': 'MISSING_USER_INFORMATION', 'code': 'D-000'},
                                    status=400)
