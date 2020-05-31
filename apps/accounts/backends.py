import json
import logging

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()
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
                user = UserModel.objects.get(email=email)
            # Create user if not exist
            except UserModel.DoesNotExist:
                user = UserModel.objects.create_user(
                    email=email,
                )
            return user

        except Exception as e:
            logger.error(e)


class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
