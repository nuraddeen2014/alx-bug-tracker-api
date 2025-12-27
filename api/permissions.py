from rest_framework.permissions import BasePermission


class OnlyAuthorEditsOrDeletes(BasePermission):
    """
    Custom permission to only allow authors of an object to edit or delete it.
    Assumes the model instance has an `created_by` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write permissions are only allowed to the author of the object.
        return obj.created_by == request.user