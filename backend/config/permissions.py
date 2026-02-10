"""
Custom permission classes for Chef Farah Ammar API.
Use role-based admin check (User.role in ('admin', 'super_admin')).
"""
from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to users with role 'admin' or 'super_admin'.
    Used for order list, order status update, and other admin-only endpoints.
    """
    message = 'Admin access required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) in ('admin', 'super_admin')
