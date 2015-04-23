from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from crowdsourcing.forms import *
from django.forms.util import ErrorList
from django.contrib.auth.decorators import login_required
import hashlib, random #, httplib2
import json, datetime
from crowdsourcing import models
from csp import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from rest_framework import status, views as rest_framework_views
from rest_framework.response import Response
import re
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from crowdsourcing.serializers import *


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def get_model_or_none(model, *args, **kwargs):
    """
        Get model object or return None, this will catch the DoesNotExist error.

        Keyword Arguments:
        model -- this is the model you want to query from
        other parameters are of variable length: e.g id=1 or username='jon.snow'

    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


class Registration(rest_framework_views.APIView):
    """
        This class handles the registration process.
    """

    def __init__(self):
        self.username = ''

    def get(self, request, *args, **kwargs):
        """
            Handles the GET method, renders the defined template with the current context
        """
        #context = self.get_context_data(**kwargs)
        #return self.render_to_response(context)
        return Response({"status":"OK"}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            Handles the POST method, this validates the registration form and if valid it will create a new user +
            user profile. Currently the emails are not enabled (EMAIL_ENABLED is set to False in the settings) so the
            account will be activated right away, otherwise this will send an activation link to the user.
        """
        #context = self.get_context_data(**kwargs)
        #form = context['form']
        json_data = json.loads(request.body.decode('utf-8'))
        form = RegistrationForm()
        form.email = json_data.get('email','')
        form.first_name = json_data.get('first_name','')
        form.last_name = json_data.get('last_name','')
        form.password1 = json_data.get('password1','')
        form.password2 = json_data.get('password2','')
        try:
            form.clean()
        except forms.ValidationError as e:
            return Response({
                'status': 'Error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)

        data = json_data
        user_check = User.objects.filter(username=data['first_name'].lower()+'.'+data['last_name'].lower())
        if not user_check:
            self.username = data['first_name'].lower()+'.'+data['last_name'].lower()
        else:
            #TODO username generating function
            self.username = data['email']
        data['username'] = self.username
        from crowdsourcing.models import RegistrationModel
        user = User.objects.create_user(data['username'],data['email'],data['password1'])
        if not settings.EMAIL_ENABLED:
            user.is_active = 1
        user.first_name = data['first_name']
        user.save()
        user_profile = models.UserProfile()
        user_profile.user = user
        user_profile.save()
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        if settings.EMAIL_ENABLED:
            if isinstance(self.username, str):
                self.username = self.username.encode('utf-8')
            activation_key = hashlib.sha1(salt.encode('utf-8')+self.username).hexdigest()
            registration_model = RegistrationModel()
            registration_model.user = User.objects.get(id=user.id)
            registration_model.activation_key = activation_key
            self.send_activation_email(email=user.email, host=request.get_host(),activation_key=activation_key)
            registration_model.save()
        return Response({
                'status': 'Success',
                'message': "Registration was successful."
            }, status=status.HTTP_201_CREATED)

    def send_activation_email(email,host,activation_key):
        """
            This sends the activation link to the user, the content will be moved to template files

            Keyword Arguments:
            host -- the domain of the website
            activation_key -- the key which activates the account
        """
        from django.core.mail import EmailMultiAlternatives

        subject, from_email, to = 'Crowdsourcing Account Activation', settings.EMAIL_SENDER, email
        activation_url = 'https://'+ host + '/account-activation/' +activation_key
        text_content = 'Hello, \n ' \
                       'Activate your account by clicking the following link: \n' + activation_url +\
                       '\nGreetings, \nCrowdsourcing Team'


        html_content = '<h3>Hello,</h3>' \
                       '<p>Activate your account by clicking the following link: <br>' \
                       '<a href="'+activation_url+'">'+activation_url+'</a></p>' \
                                                                      '<br><br> Greetings,<br> <strong>crowdresearch App Team</strong>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

class Login(rest_framework_views.APIView):
    """
        This class handles the login process, it checks the user credentials and if redirected from another page
        it will redirect to that page after the login is done successfully.
    """


    def __init__(self):
        self.status = 200
        self.redirect_to = ''
        self.user = None
        self.username = ''
    '''
    def get_context_data(self, **kwargs):
        if settings.PYTHON_VERSION == 3:
            pass
            #context = super().get_context_data(**kwargs)
        else:
            context = super(Login,self).get_context_data(**kwargs)
        context['form'] = LoginForm(self.request.POST or None)
        return context
    '''

    def get(self, request, *args, **kwargs):
        """
            Renders the login form, if the user is already authenticated will redirect to
            the user profile (later to be changed to Home)
        """
        '''
        if self.request.user.is_authenticated():
            return HttpResponseRedirect('/users/'+self.request.user.username)
        context = self.get_context_data(**kwargs)
        #form = LoginForm(self.request.POST or None)
        return self.render_to_response(context)
        '''
        return Response({"status":"OK"}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            This handles the login POST method, it enables the user to login with username or password.
        """

        data = json.loads(request.body.decode('utf-8'))

        email = data.get('username', '')
        password = data.get('password', '')

        from django.contrib.auth import authenticate, login
        self.redirect_to = request.POST.get('next', '') #to be changed, POST does not contain any data
        email_or_username = email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_or_username):
            self.username = email_or_username
        else:
            user = get_model_or_none(User,email=email_or_username)
            if user is not None:
                self.username = user.username

        self.user = authenticate(username=self.username, password=password)
        if self.user is not None:
            if self.user.is_active:
                login(request, self.user)
                serializer = UserSerializer(self.user)
                return Response(serializer.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'Account is not activated yet.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
            'status': 'Unauthorized',
            'message': 'Username or password is incorrect.'
        }, status=status.HTTP_401_UNAUTHORIZED)


class Logout(rest_framework_views.APIView):

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class UserProfile(rest_framework_views.APIView):
    """
        This class handles user profile rendering, changes and so on.

    """

    def __init__(self):
        self.user_profile = None

    def dispatch(self, *args, **kwargs):
        """
            This is necessary because all the methods of this class need to be protected with login_required decorator.
        """
        return super(UserProfile,self).dispatch(*args, **kwargs)


    def get(self, request, *args, **kwargs):
        """
            Gets the requested user profile and passes it to the template.
            If the user profile does not exist it will render the 404 page.

            Keyword Arguments:
            kwargs['username'] -- the username from the URL
        """
        #self.user_profile = get_model_or_none(models.UserProfile, username=kwargs['username'])
        '''
        if self.user_profile is None:
            return Response({
                'status': 'not found',
                'message': 'user profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        friends = self.user_profile.friends.all()
        return Response({
            'user': self.user_profile,
            'friends': friends
        })
        '''
        profile = get_model_or_none(models.UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile)
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