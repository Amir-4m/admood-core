import logging

from celery import shared_task
from django.conf import settings

from admood_core.settings import SITE_URL, EMAIL_VERIFICATION_URI
from apps.core.utils.mail import Mail

logger = logging.getLogger('admood_core.accounts')


@shared_task
def send_verification_email(email_address, code):
    verify_url = '{SITE_URL}/{EMAIL_VERIFICATION_URI}/?code={CODE}&email={EMAIL}' \
        .format(SITE_URL=SITE_URL,
                EMAIL_VERIFICATION_URI=EMAIL_VERIFICATION_URI,
                CODE=code,
                EMAIL=email_address)
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
