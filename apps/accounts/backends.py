import json
import logging

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()
logger = logging.getLogger('admood_core.accounts')


class GoogleAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": password})
            data = json.loads(response.text)

            if data['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('wrong issuer.')

            email = data['email']
            if username != email:
                raise ValueError('email not match.')

            try:
                user = User.objects.get(email=email)
            # Create user if not exist
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                )
            return user

        except Exception as e:
            logger.error(e)
            pass
