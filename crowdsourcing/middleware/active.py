from django.utils import timezone


class CustomActiveViewMiddleware():
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if not request.user.is_anonymous() and request.path == '/':
            userprofile = request.user.profile
            userprofile.last_active = timezone.now()
            userprofile.save()
