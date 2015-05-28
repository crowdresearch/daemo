__author__ = 'dmorina'
from csp import settings


def send_activation_email(email, host, activation_key):
        """
            This sends the activation link to the user, the content will be moved to template files

            Keyword Arguments:
            host -- the domain of the website
            activation_key -- the key which activates the account
        """
        #from django.core.mail import EmailMultiAlternatives
        import smtplib
        subject, from_email, to = 'Crowdsourcing Account Activation', settings.EMAIL_SENDER, email
        activation_url = 'http://'+ host + '/account-activation/' +activation_key
        text_content = 'Hello, \n ' \
                       'Activate your account by clicking the following link: \n' + activation_url +\
                       '\nGreetings, \nCrowdsourcing Team'


        html_content = '<h3>Hello,</h3>' \
                       '<p>Activate your account by clicking the following link: <br>' \
                       '<a href="'+activation_url+'">'+activation_url+'</a></p>' \
                                                                      '<br><br> Greetings,<br> <strong>Crowdsourcing Team</strong>'
        #msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        #msg.attach_alternative(html_content, "text/html")
        #msg.send()
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(settings.EMAIL_SENDER, settings.EMAIL_SENDER_PASSWORD)
            server.sendmail(settings.EMAIL_SENDER, to, text_content)
            server.close()
        except:
            pass #log