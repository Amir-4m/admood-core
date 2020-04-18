import logging

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from google.auth.transport import requests
from google.oauth2 import id_token

User = get_user_model()
logger = logging.getLogger('admood_core.accounts')


class GoogleAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            id_info = id_token.verify_oauth2_token(password, requests.Request())

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            email = id_info['email']

            if username != email:
                logger.error("Email is not match")
                return

            try:
                user = User.objects.get(email=email)

            # Create user if not exist
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                )

            return user

        except ValueError:
            logger.error("Invalid google token.")
            # Invalid token
            pass
