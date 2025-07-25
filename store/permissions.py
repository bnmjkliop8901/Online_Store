from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            if not request.user.is_authenticated or not getattr(request.user, 'is_seller', False):
                return False
        return True