import logging

from celery import shared_task
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage

from admood_core.settings import SITE_URL, USER_VERIFICATION_URL, USER_RESET_PASSWORD_URL
from apps.core.utils.mail import Mail
from apps.core.utils.sms import api_send_sms

logger = logging.getLogger(__file__)


@shared_task
def send_verification_email(email_address, code):
    logger.info(f'sending verification email {email_address}')

    verify_url = f'{SITE_URL}/{USER_VERIFICATION_URL}/?rc={code}'
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
    logger.info(f'Sending reset password {email_address}')

    url = f'{SITE_URL}/{USER_RESET_PASSWORD_URL}/?rc={code}'
    message = EmailMessage('reset password', url, to=[email_address], from_email=settings.EMAIL_HOST_USER)

    with mail.get_connection() as connection:
        connection.send_messages([message])
        logger.info(f'Reset password sent url: {url}')


@shared_task
def send_verification_sms(phone_number, text):
    api_send_sms(phone_number, text)
