from crowdsourcing.forms import *
from csp import settings
from rest_framework import status, views as rest_framework_views, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib, random
from crowdsourcing.serializers.project import *
from crowdsourcing.models import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.serializers.user import UserProfileSerializer, UserSerializer
from django.contrib.auth.models import User


class UserViewSet(viewsets.ModelViewSet):
    """
        This class handles user view sets
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    '''
    def create(self, request, *args, **kwargs):
        self.queryset = User.objects.all()
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():# and serializer.is_valid_extended():
            #return UserSerializer.create(serializer.validated_data)
            return Response(serializer.errors)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    '''
    detail_route(methods=['post'])
    def register(self, request, *args, **kwargs):
        json_data = json.loads(request.body.decode('utf-8'))
        return UserProfileSerializer.create(json_data)
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
        user.last_name = data['last_name']
        user.save()
        user_profile = UserProfile()
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
            #self.send_activation_email(email=user.email, host=request.get_host(),activation_key=activation_key)
            registration_model.save()
        return Response({
                'status': 'Success',
                'message': "Registration was successful."
            }, status=status.HTTP_201_CREATED)
    '''
    def send_activation_email(self,email,host,activation_key):
        """
            This sends the activation link to the user, the content will be moved to template files

            Keyword Arguments:
            host -- the domain of the website
            activation_key -- the key which activates the account
        """
        from django.core.mail import EmailMultiAlternatives
        import smtplib
        subject, from_email, to = 'Crowdsourcing Account Activation', settings.EMAIL_SENDER, email
        activation_url = 'http://'+ host + '/account-activation/' +activation_key
        text_content = 'Hello, \n ' \
                       'Activate your account by clicking the following link: \n' + activation_url +\
                       '\nGreetings, \nCrowdsourcing Team'


        html_content = '<h3>Hello,</h3>' \
                       '<p>Activate your account by clicking the following link: <br>' \
                       '<a href="'+activation_url+'">'+activation_url+'</a></p>' \
                                                                      '<br><br> Greetings,<br> <strong>crowdresearch App Team</strong>'
        #msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        #msg.attach_alternative(html_content, "text/html")
        #msg.send()
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(settings.EMAIL_SENDER, settings.EMAIL_SENDER_PASSWORD)
            server.sendmail(settings.EMAIL_SENDER, to, text_content)
            #server.quit()
            server.close()
            print 'successfully sent the mail'
        except:
            print "failed to send mail"
    '''
