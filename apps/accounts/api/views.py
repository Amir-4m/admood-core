from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication


class HelloView(APIView):
    # authentication_classes = (JWTAuthentication,)
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

