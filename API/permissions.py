from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.views import APIView

class IsAdminGroup(BasePermission):
    """
    Allows access only to users in the 'admin' group.
    """
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # flat changes output from list of tuples to list of strings
        if 'admin' in request.user.groups.values_list('name', flat=True):
            return True
        # if request.user.groups.filter(name='admin').exists():
            # return True

        return False

class CustomTokenPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        
        auth = JWTAuthentication()

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise PermissionDenied("Missing or invalid Authorization header.")

            validated_token = auth.get_validated_token(request.headers.get('Authorization').split()[1])
            token_type = validated_token.get('custom_token_type')


            if request.method in ['PUT', 'PATCH'] and token_type not in ['admin', 'cafe_owner']:
                return False
            
            if request.method == 'POST' and token_type not in ['admin', 'cafe_owner']:
                return False

            if request.method == 'DELETE' and token_type != 'admin':
                return False

            return True
        except Exception:
            raise PermissionDenied("Invalid or missing token.")
