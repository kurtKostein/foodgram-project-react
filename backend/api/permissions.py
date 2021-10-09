from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.is_staff:
            return True
        return False


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if (
                request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_staff
        ):
            return True
        return False
