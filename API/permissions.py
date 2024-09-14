from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

class IsAdminGroup(BasePermission):
    """
    Allows access only to users in the 'admin' group.
    """
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        if 'admin' in request.user.groups.values_list('name', flat=True):
            return True

        return False
