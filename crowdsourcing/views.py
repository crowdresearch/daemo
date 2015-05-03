#from provider.oauth2.models import RefreshToken, AccessToken
from crowdsourcing import models
from crowdsourcing.forms import *
from crowdsourcing.utils import *
from csp import settings
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework import generics
from rest_framework import status, views as rest_framework_views, viewsets
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

import hashlib, random
import re
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from crowdsourcing.serializers.user import *
from crowdsourcing.serializers.requester import *
from crowdsourcing.serializers.project import *
from crowdsourcing.utils import *
from crowdsourcing.models import *
from rest_framework.decorators import detail_route, list_route

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


class UserProfileViewSet(viewsets.ModelViewSet):
    """
        This class handles user profile rendering, changes and so on.
    """
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'
    @detail_route(methods=['post'])
    def update_profile(self, request, user__username=None):
        serializer = UserProfileSerializer(data=request.data)
        user_profile = self.get_object()
        if serializer.is_valid():
            serializer.update(user_profile,serializer.validated_data)

            return Response({'status': 'updated profile'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route()
    def get_profile(self, request):
        user_profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(user_profiles)
        return Response(serializer.data)

class ForgotPassword(rest_framework_views.APIView):
    """
        This takes care of the forgot password process.
    """
    '''
    def get_context_data(self, **kwargs):
        context = super(ForgotPassword,self).get_context_data(**kwargs)
        context['form'] = ForgotPasswordForm(self.request.POST or None)
        return context
    '''
    def get(self, request, *args, **kwargs):
        '''
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
        '''
        return Response({"status":"OK"}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            Here we process the POST and if the form is valid (i.e email is valid)
            then we send a password reset link to the user.
        """
        email = json.loads(request.body.decode('utf-8')).get('email','')
        form = ForgotPasswordForm()
        form.email = email
        #temporary check, will be done properly
        try:
            form.clean()
        except forms.ValidationError:
            return Response({
                'status': 'Error',
                'message': 'Invalid email entered.'
            }, status=status.HTTP_404_NOT_FOUND)

        from crowdsourcing.models import PasswordResetModel

        user = User.objects.get(email=email)
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        username = user.username
        reset_key = hashlib.sha1(str(salt+username).encode('utf-8')).hexdigest()
        password_reset = PasswordResetModel()
        password_reset.user = user
        password_reset.reset_key = reset_key
        if settings.EMAIL_ENABLED:
            password_reset.save()
            self.send_password_reset_email(email=email, host=request.get_host(), reset_key=reset_key)
        return Response({
                'status': 'Success',
                'message': 'Email sent.'
            }, status=status.HTTP_201_CREATED)
        #return render(request,'registration/password_reset_email_sent.html')
        #context['form'] = form
        #return self.render_to_response(context)

    #TODO timer for the reset key
    #TODO HTML templates should be moved to files
    def send_password_reset_email(email, host, reset_key):
        """
            This sends the email to the user, it will be moved to a new class in the future so that all emails are
            processed by one class.
            The email includes two links, one for changing the password and the other for discarding the forgot password request.
        """
        from django.core.mail import EmailMultiAlternatives

        subject, from_email, to = 'Crowdsourcing Password Reset', settings.EMAIL_SENDER, email
        reset_url = 'https://'+ host + '/reset-password/' +reset_key
        text_content = 'Hello, \n ' \
                       'Please reset your password using the following link: \n' + reset_url+'/1' \
                       '\nIf you did not request a password reset please click the following link: ' +reset_url+'/0' \
                       '\nGreetings, \nCrowdsourcing Team'


        html_content = '<h3>Hello,</h3>' \
                       '<p>Please reset your password using the following link: <br>' \
                       '<a href="'+reset_url+'/1'+'">'+reset_url+'/1'+'</a></p>' \
                                                                    "<br><p>If you didn't request a password reset please click the following link: <br>" + '' \
                                                                    '<a href="'+reset_url+'/0'+'">'+reset_url+'/0'+'</a><br><br> Greetings,<br> <strong>Crowdsourcing Team</strong>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class Oauth2TokenView(rest_framework_views.APIView):

    def post(self, request, *args, **kwargs):
        oauth2_login = Oauth2Utils()
        response_data, oauth2_status = oauth2_login.get_token(request)
        return Response(response_data,status=oauth2_status)


#Will be moved to Class Views
#################################################
def registration_successful(request):
    return render(request,'registration/registration_successful.html')

def home(request):
    return render(request,'index.html')

def activate_account(request, activation_key):
    """
        this handles the account activation after the user follows the link from his/her email.
    """
    from django.contrib.auth.models import User
    try:
        activate_user = models.RegistrationModel.objects.get(activation_key=activation_key)
        if activate_user:
            usr = User.objects.get(id=activate_user.user_id)
            usr.is_active = 1
            usr.save()
            activate_user.delete()
            return render(request,'registration/registration_complete.html')
    except:
        return HttpResponseRedirect('/')

#TODO check expired keys
def reset_password(request, reset_key, enable):
    """
        Resets the user password if requested from the user.
    """
    from crowdsourcing.models import PasswordResetModel
    #this must be changed for angular support
    form = PasswordResetForm(request.POST or None)
    if enable == "1":
        pass
        #return render(request, 'registration/ignore_password_reset.html')
    elif enable == "0":
        try:
            password_reset = PasswordResetModel.objects.get(reset_key=reset_key)
            password_reset.delete()
        except:
            pass
        return render(request, 'registration/ignore_password_reset.html')
    if request.method == 'POST' and form.is_valid():
        #try:
        password_reset = PasswordResetModel.objects.get(reset_key=reset_key)
        user = User.objects.get(id = password_reset.user_id)
        user.set_password(request.POST['password1'])
        user.save()
        password_reset.delete()
        return render(request, 'registration/password_reset_successful.html')
    return render(request, 'registration/reset_password.html',{'form':form})
#################################################
