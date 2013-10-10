
from mailqueue.models import MailerMessage


def send_mail(subject, message, from_email, recipient_list, html_message=None, internal_sender_id=None):
    """
    Simplified version of the send_mail function which queues e-mails in the mail queue

    """

    for recipient in recipient_list:

        new_message = MailerMessage()
        new_message.subject = subject
        new_message.to_address = recipient
        new_message.from_address = from_email
        new_message.content = message

        if html_message is not None:
            new_message.html_content = html_message

        if internal_sender_id is None:
            new_message.app = "selvbetjening"
        else:
            new_message.app = internal_sender_id

        new_message.save()