import django.contrib.auth
from datetime import datetime

class CustomLoginViewMiddleware():
	def process_view(self, request, callback, callback_args, callback_kwargs):
		if not request.user.is_anonymous() and request.path == '/':
			user = request.user
			user.last_login = datetime.now()
			user.save()
