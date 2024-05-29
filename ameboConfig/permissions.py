from rest_framework import permissions
from users.models import AppUsers

class Registration(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True

        return request.user and request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        app_user = AppUsers.objects.get(owner=request.user)
        return (request.user.is_authenticated and app_user.user_type == "admin") or request.method in permissions.SAFE_METHODS


