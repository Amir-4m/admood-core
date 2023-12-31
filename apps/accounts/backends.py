from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from apps.accounts.models import Verification

UserModel = get_user_model()


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
        Reject users with is_verified=False and is_active=False.
        """
        is_active = getattr(user, 'is_active', None)
        is_verified = getattr(user, 'is_verified')
        return is_verified and (is_active or is_active is None)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(phone_number=username)
        except (UserModel.DoesNotExist, ValueError):
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            verification = Verification.verify_user_by_phone_number(user=user, verify_code=password)
            if verification:
                user.verify()
                if verification.reset_password:
                    user.set_unusable_password()
                user.save()
                if self.user_can_authenticate(user):
                    return user
