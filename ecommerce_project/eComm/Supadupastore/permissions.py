from rest_framework import permissions


class IsVendor(permissions.BasePermission):
    """
    Custom permission to only allow vendors to create/edit stores and products.
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for vendors
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='Vendors').exists()


class IsStoreOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a store to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the store
        return obj.owner == request.user


class IsProductOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a product (through store) to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the store
        return obj.store.owner == request.user
