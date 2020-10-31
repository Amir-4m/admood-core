import logging

from celery import shared_task
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage

from admood_core.settings import SITE_URL, USER_VERIFICATION_URL, USER_RESET_PASSWORD_URL
from apps.core.utils.mail import Mail
from apps.core.utils.sms import api_send_sms

logger = logging.getLogger('admood_core.accounts')


@shared_task
def send_verification_email(email_address, code):
    verify_url = f'{SITE_URL}/{USER_VERIFICATION_URL}?rc={code}'

    context = {
        'lang': 'fa',  # if settings.LANGUAGE_CODE.lower() == 'fa-ir' else 'en',
        'base_url': "127.0.0.1",
        'page_title': "تایید",
        'project_name': "admood",

        'username': email_address,
        'verify_url': verify_url,
        'verification_code': code,
        'has_password': True,
    }

    mail = Mail(settings.EMAIL_HOST_USER)
    mail.send_messages(subject="verification",
                       template="accounts/email/verify.html",
                       context=context,
                       to_emails=[email_address])


@shared_task
def send_reset_password(email_address, code):
    url = f'{SITE_URL}/{USER_RESET_PASSWORD_URL}/?rc={code}'
    message = EmailMessage('reset password', url, to=[email_address], from_email=settings.EMAIL_HOST_USER)
    connection = mail.get_connection()
    connection.open()
    connection.send_messages([message])
    connection.close()


@shared_task
def send_verification_sms(phone_number, text):
    try:
        api_send_sms(phone_number, text)
    except:
        raise
