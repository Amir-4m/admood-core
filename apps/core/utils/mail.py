from django.core import mail
from django.core.mail import EmailMessage
from django.template.loader import get_template


class Mail(object):
    """
    Send email messages helper class
    """

    def __init__(self, from_email=None):
        self.connection = mail.get_connection()
        self.from_email = from_email

    def send_messages(self, subject, template, context, to_emails):
        """
        Send email messages
        :param subject: email subject
        :param template: email template that contains placeholder that consume context param
        :param context: actual data for email template placeholders
        :param to_emails: emails that send the confirmation message to them
        """
        messages = self.__generate_messages(subject, template, context, to_emails)
        self.__send_mail(messages)

    def __send_mail(self, mail_messages):
        """
        Send email messages
        :param mail_messages:
        """
        self.connection.open()
        self.connection.send_messages(mail_messages)
        self.connection.close()

    def __generate_messages(self, subject, template, context, to_emails):
        """
        Generate email message from Django template
        :param subject: email message subject
        :param template: email template
        :param to_emails: to email address[es]
        :returns messages: prepared messages list
        """
        messages = []
        message_template = get_template(template)
        for recipient in to_emails:
            message_content = message_template.render(context)
            message = EmailMessage(subject, message_content, to=[recipient], from_email=self.from_email)
            message.content_subtype = 'html'
            messages.append(message)

        return messages
