from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_mail(email_from, email_to, subject, text_content, html_content):
    mail = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=email_from,
        to=[email_to]
    )

    mail.attach_alternative(html_content, "text/html")
    mail.send()


def send_activation_email(email, host, activation_key):
    email_from = 'Daemo Team <%s>' % settings.EMAIL_SENDER
    email_to = email
    subject = 'Daemo Account Activation'
    activation_url = 'http://' + host + '/account-activation/' + activation_key
    text_content = 'Hello, \n ' \
                   'Activate your account by clicking the following link: \n' + activation_url + \
                   '\nGreetings, \nDaemo Team'

    html_content = '<h3>Hello,</h3>' \
                   '<p>Activate your account by clicking the following link: <br>' \
                   '<a href="' + activation_url + '">' + activation_url \
                   + '</a></p>' + '<br><br> Greetings,<br> <strong>Daemo Team</strong>'

    send_mail(email_from, email_to, subject, text_content, html_content)


def send_password_reset_email(email, host, reset_key):
    """
        This sends the email to the user
        The email includes two links, one for changing the password and the other for discarding the forgot password
        request.
    """
    email_from = 'Daemo Team <%s>' % settings.EMAIL_SENDER
    email_to = email
    subject = 'Daemo Password Reset'
    reset_url = 'http://' + host + '/reset-password/' + reset_key
    text_content = 'Hello, \n ' \
                   'Please reset your password using the following link: \n' + reset_url + '/1'' \
                   ''\nIf you did not request a password reset please click the following link: ' + reset_url + '/0'' \
                   ''\nGreetings, \nDaemo Team'
    html_content = '<h3>Hello,</h3>' \
                   '<p>Please reset your password using the following link: <br>' \
                   '<a href="' + reset_url + '/1' + '">' + reset_url + '/1' + '</a></p>'" \
                   ""<br><p>If you didn't request a password reset please click the following link: <br>" + \
                   '<a href="' + reset_url + '/0' + '">' + reset_url + '/0' + \
                   '</a><br><br> Greetings,<br> <strong>Daemo Team</strong>'

    send_mail(email_from, email_to, subject, text_content, html_content)
