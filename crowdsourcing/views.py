from django.shortcuts import render
from rest_framework import views as rest_framework_views
from rest_framework.views import APIView
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from rest_framework.response import Response

from crowdsourcing.serializers.user import *
from crowdsourcing.serializers.project import *
from crowdsourcing.utils import *
from crowdsourcing.models import *
from crowdsourcing.utils import get_model_or_none


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class Logout(APIView):
    def post(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class Login(APIView):
    method_decorator(csrf_protect)

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import authenticate as auth_authenticate, login
        # self.redirect_to = request.POST.get('next', '') #to be changed, POST does not contain any data

        username = request.data.get('username', '')
        password = request.data.get('password', '')
        email_or_username = username

        # match with username if not email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_or_username):
            username = email_or_username
        else:
            user = get_model_or_none(User, email=email_or_username)
            if user is not None:
                username = user.username

        user = auth_authenticate(username=username, password=password)

        if user is not None:

            if not user.is_anonymous():
                userprofile = user.userprofile
                userprofile.last_active = timezone.now()
                userprofile.save()

            if user.is_active:
                login(request, user)
                response_data = dict()
                response_data["username"] = user.username
                response_data["email"] = user.email
                response_data["first_name"] = user.first_name
                response_data["last_name"] = user.last_name
                response_data["date_joined"] = user.date_joined
                response_data["last_login"] = user.last_login
                response_data["is_requester"] = hasattr(request.user.userprofile, 'requester')
                response_data["is_worker"] = hasattr(request.user.userprofile, 'worker')

                return Response(response_data, status.HTTP_200_OK)
            else:
                raise AuthenticationFailed(_('Account is not activated yet.'))
        else:
            raise AuthenticationFailed(_('Username or password is incorrect.'))


class Oauth2TokenView(rest_framework_views.APIView):
    def post(self, request, *args, **kwargs):
        oauth2_login = Oauth2Utils()
        response_data, oauth2_status = oauth2_login.get_token(request)
        return Response(response_data, status=oauth2_status)


# Will be moved to Class Views
#################################################
def registration_successful(request):
    return render(request, 'registration/registration_successful.html')


def home(request):
    if request.user.is_authenticated():
        return render(request, 'index.html')
    # return render(request, 'homepage.html')
    return render(request, 'index.html')
