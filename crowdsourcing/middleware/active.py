from datetime import datetime


class CustomActiveViewMiddleware():
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if not request.user.is_anonymous() and request.path == '/':
            userprofile = request.user.userprofile
            userprofile.last_active = datetime.now()
            userprofile.save()
