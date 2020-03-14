import requests
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class LoginAPIView(APIView):

    def mobile_authenticate(self):
        pass

    def email_authenticate(self):
        pass

    def post(self, request):
        pass


class ConfirmLoginAPIView(APIView):
    def post(self, request):
        pass


class GoogleAPIView(APIView):
    def post(self, request):
        payload = {'access_token': request.data.get("token")}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)

        if 'error' in data:
            content = {'message': 'invalid google token'}
            return Response(content)

        # create user if not exist
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            user = User()
            user.username = data['email']
            # provider random default password
            user.password = make_password(BaseUserManager().make_random_password())
            user.email = data['email']
            user.save()

        token = RefreshToken.for_user(user)  # generate token without username & password
        data = {
            'access_token': str(token.access_token),
            'refresh_token': str(token)
        }
        return Response(data=data)
