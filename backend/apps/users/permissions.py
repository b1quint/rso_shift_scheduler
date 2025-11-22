from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to anonymous users.
    Authenticated users have full access (read and write).
    
    - GET, HEAD, OPTIONS: Allowed for everyone (anonymous and authenticated)
    - POST, PUT, PATCH, DELETE: Require authentication
    """
    
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require authentication for write operations
        return request.user and request.user.is_authenticated
