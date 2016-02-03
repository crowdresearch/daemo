from email.mime.base import MIMEBase

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address, EmailMultiAlternatives

import sendgrid


class SendGridBackend(BaseEmailBackend):
    """
    A wrapper for SendGrid mailer
    """

    def __init__(self, fail_silently=False, **kwargs):
        super(SendGridBackend, self).__init__(fail_silently=fail_silently)
        self.api_key = getattr(settings, "SENDGRID_API_KEY", None)

        if self.api_key is None:
            raise ImproperlyConfigured('''SENDGRID_API_KEY not declared in settings.py''')

        self.client = sendgrid.SendGridClient(
            self.api_key,
            raise_errors=not fail_silently)

    def open(self):
        pass

    def close(self):
        pass

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            try:
                mail = self._create_mail(message)
                if mail:
                    self.client.send(mail)
                    num_sent += 1
            except sendgrid.SendGridClientError:
                if not self.fail_silently:
                    raise
            except sendgrid.SendGridServerError:
                if not self.fail_silently:
                    raise
        return num_sent

    def _create_mail(self, email):
        """A helper method that creates mail for sending."""
        if not email.recipients():
            return False

        from_email = sanitize_address(email.from_email, email.encoding)
        recipients = [sanitize_address(addr, email.encoding)
                      for addr in email.recipients()]

        mail = sendgrid.Mail()
        mail.add_to(recipients)
        mail.add_cc(email.cc)
        mail.add_bcc(email.bcc)
        mail.set_text(email.body)
        mail.set_subject(email.subject)
        mail.set_from(from_email)

        if isinstance(email, EmailMultiAlternatives):
            for alt in email.alternatives:
                if alt[1] == "text/html":
                    mail.set_html(alt[0])

        for attachment in email.attachments:
            if isinstance(attachment, MIMEBase):
                mail.add_attachment_stream(
                    attachment.get_filename(),
                    attachment.get_payload())
            elif isinstance(attachment, tuple):
                mail.add_attachment_stream(attachment[0], attachment[1])

        return mail
