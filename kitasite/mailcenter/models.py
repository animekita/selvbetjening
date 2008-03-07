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
        """ 
        Send e-mails to a list of e-mail adresses.
        
        """
        mails = []
        
        for recipient in recipients:
            body_html = render_to_string('mailcenter/email/newsletter_html.txt',
                                   { 'body': self.body })
            mail = EmailMultiAlternatives(self.subject, self.body, settings.DEFAULT_FROM_EMAIL, [recipient])
            mail.attach_alternative(body_html, "text/html")
            mails.append(mail)

        connection = SMTPConnection()
        connection.send_messages(mails)
    
    def send_mail_to_users(self, users):
        """ 
        Sends mails to a list of users, while registering the list of users in the recipients
        relation.
        
        """
        emails = []
        for user in users:
            emails.append(user.email)
            self.recipients.add(user)
        self.send_mail(emails)
    
    def recipient_filter(self, recipients):
        """
        Filter a list of recipient users, dividing them into an "accept" and a "deny" group based
        on previous send e-mail to those users. A touple containing two lists are returned.
        ([accept], [deny])
        
        """
        accept = []
        deny = []
        current_recipients = self.recipients.all()
        for recipient in recipients:
            if recipient in current_recipients:
                deny.append(recipient)
            else:
                accept.append(recipient)
        
        return (accept, deny)
    
    class Admin:
        pass
    