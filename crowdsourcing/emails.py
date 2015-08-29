from csp import settings


def send_activation_email_gmail(email, host, activation_key):
    """
        This sends the activation link to the user using Gmail, the content will be moved to template files

        Keyword Arguments:
        host -- the domain of the website
        activation_key -- the key which activates the account
    """
    import smtplib

    subject, from_email, to = 'Daemo Account Activation', settings.EMAIL_SENDER, email
    activation_url = 'http://' + host + '/account-activation/' + activation_key
    text_content = 'Hello, \n ' \
                   'Activate your account by clicking the following link: \n' + activation_url + \
                   '\nGreetings, \nDaemo Team'

    html_content = '<h3>Hello,</h3>' \
                   '<p>Activate your account by clicking the following link: <br>' \
                   '<a href="' + activation_url + '">' + activation_url + '</a></p>' \
                                                                          '<br><br> Greetings,<br> <strong>Daemo Team</strong>'
    message = 'Subject: %s\n\n%s' % (subject, text_content)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(settings.EMAIL_SENDER_DEV, settings.EMAIL_SENDER_PASSWORD_DEV)
        server.sendmail(from_email, to, message)
        server.close()
    except:
        print("Error sending activation email")


def send_activation_email_sendgrid(email, host, activation_key):
    """
        This sends the activation link to the user using sendgrid, the content will be moved to template files

        Keyword Arguments:
        host -- the domain of the website
        activation_key -- the key which activates the account
    """
    # from django.core.mail import EmailMultiAlternatives
    import smtplib

    subject, from_email, to = 'Daemo Account Activation', settings.EMAIL_SENDER, email
    activation_url = 'http://' + host + '/account-activation/' + activation_key
    text_content = 'Hello, \n ' \
                   'Activate your account by clicking the following link: \n' + activation_url + \
                   '\nGreetings, \nDaemo Team'

    html_content = '<h3>Hello,</h3>' \
                   '<p>Activate your account by clicking the following link: <br>' \
                   '<a href="' + activation_url + '">' + activation_url + '</a></p>' \
                                                                          '<br><br> Greetings,<br> <strong>Daemo Team</strong>'
    send_grid(to, subject, text_content, html_content)

def send_grid(to, subject, text, html=None):
    import sendgrid
    sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY)

    message = sendgrid.Mail()
    message.add_to('<%s>'%to)
    message.set_subject(subject)
    message.set_text(text)
    message.set_html(html)
    message.set_from('Daemo Team <%s>'%settings.EMAIL_SENDER)
    status, msg = sg.send(message)
    return status, msg