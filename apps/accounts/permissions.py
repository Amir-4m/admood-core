from rest_framework.permissions import IsAuthenticated


class CustomIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and
                    request.user.is_verified and request.user.is_authenticated)
