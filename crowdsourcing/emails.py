from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string


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
    subject = 'Daemo account activation'
    activation_url = 'http://' + host + '/account-activation/' + activation_key
    text_content = 'Welcome to Daemo! To finish activating your account and complete registration, click here: \n' + \
                   activation_url + \
                   '\n \n- The Daemo Team'

    html_content = '<p>Welcome to Daemo! To finish activating your account and complete registration, ' \
                   'click here:  <br>' \
                   '<a href="' + activation_url + '">' + activation_url \
                   + '</a></p>' + '<br><br><br>- The Daemo Team</strong>'

    send_mail(email_from, email_to, subject, text_content, html_content)


def send_password_reset_email(email, host, reset_key):
    """
        This sends the email to the user
        The email includes two links, one for changing the password and the other for discarding the forgot password
        request.
    """
    email_from = 'Daemo Team <%s>' % settings.EMAIL_SENDER
    email_to = email
    subject = 'Daemo password reset'
    reset_url = 'http://' + host + '/reset-password/' + reset_key
    text_content = 'Please reset your password using the following link: \n' + reset_url + '/1'' \
                   ''\nIf you did not request a password reset please click the following link: ' + reset_url + '/0'' \
                   ''\n \n - The Daemo Team'
    html_content = '<p>Please reset your password using the following link: <br>' \
                   '<a href="' + reset_url + '/1' + '">' + reset_url + '/1' + '</a></p>'" \
                   ""<br><p>If you didn't request a password reset please click the following link: <br>" + \
                   '<a href="' + reset_url + '/0' + '">' + reset_url + '/0' + \
                   '</a><br><br><br>- The Daemo Team'

    send_mail(email_from, email_to, subject, text_content, html_content)


def send_notifications_email(email, url, messages):
    email_from = 'Daemo Team <%s>' % settings.EMAIL_SENDER
    email_to = email
    subject = '[Daemo] Notifications on Daemo while you were away'
    context = Context({
        'email_from': email_from,
        'email_to': email_to,
        'subject': subject,
        'url': url,
        'sender_list': messages
    })
    text_content = render_to_string('emails/notifications.txt', context)
    html_content = render_to_string('emails/notifications.html', context)
    send_mail(email_from, email_to, subject, text_content, html_content)


def send_new_tasks_email(to, requester_handle, project_name, price, project_id, available_tasks):
    email_from = 'Daemo Team <%s>' % settings.EMAIL_SENDER
    subject = 'New Daemo task available: {}'.format(project_name)
    context = Context({
        'unsubscribe_url': settings.SITE_HOST + '/unsubscribe',
        'project_url': settings.SITE_HOST + '/task-feed/{}'.format(project_id),
        'owner_handle': requester_handle,
        'available_tasks': available_tasks,
        'project_price': price,
        'project_name': project_name
    })
    text_content = render_to_string('emails/new-tasks-available.txt', context)
    html_content = render_to_string('emails/new-tasks-available.html', context)
    send_mail(email_from, to, subject, text_content, html_content)
