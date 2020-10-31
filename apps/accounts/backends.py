import json
import logging

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from apps.accounts.models import Verification

UserModel = get_user_model()
logger = logging.getLogger('admood_core.accounts')


# class GoogleAuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": password})
#             data = json.loads(response.text)
#
#             if data['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
#                 raise ValueError('wrong issuer.')
#
#             email = data['email']
#             if username != email:
#                 raise ValueError('email not match.')
#
#             try:
#                 user = UserModel.objects.get(email=email)
#             # Create user if not exist
#             except UserModel.DoesNotExist:
#                 user = UserModel.objects.create_user(
#                     email=email,
#                     is_verified=True,
#                 )
#             return user
#
#         except:
#             return


class EmailAuthBackend(ModelBackend):

    def user_can_authenticate(self, user):
        """
        Reject users with is_verified=False and is_active=False.
        """
        is_active = getattr(user, 'is_active', None)
        is_verified = getattr(user, 'is_verified')
        return is_verified and (is_active or is_active is None)

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


class PhoneAuthBackend(ModelBackend):

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False.
        """
        is_active = getattr(user, 'is_active')
        return is_active

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(phone_number=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            verification = Verification.get_valid(user=user, verify_code=password)
            if verification:
                verification.verify()
                verification.save()
                user.verify()
                if self.user_can_authenticate(user):
                    if verification.reset_password:
                        user.set_unusable_password()
                    user.save()
                    return user
