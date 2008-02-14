from django.conf import settings
from django.db import models
from django.core.mail import EmailMultiAlternatives, SMTPConnection
from django.contrib.auth.models import User
from django.template.loader import render_to_string

# Create your models here.

class Mail(models.Model):
    subject = models.CharField(max_length=128)
    body = models.TextField()
    date_created = models.DateField()
    recipients = models.ManyToManyField(User, editable=False)
    
    def is_draft(self):
        return (len(self.recipients.all()) == 0)
    
    def send_mail(self, recipients):
        
        mails = []
        
        for recipient in recipients:
            body_html = render_to_string('mailcenter/email/newsletter_html.txt',
                                   { 'body': self.body })
            mail = EmailMultiAlternatives(self.subject, self.body, settings.DEFAULT_FROM_EMAIL, [recipient])
            mail.attach_alternative(body_html, "text/html")
            mails.append(mail)

        connection = SMTPConnection()
        connection.send_messages(mails)
    
    class Admin:
        pass
    