from __future__ import unicode_literals

from rest_framework import permissions


# Used instead of the original DjangoModelPermissions in rest_serializer.permissions
# Ensures that custom permissions are considered before permission is denied

class DjangoModifiedModelPermissions(permissions.DjangoModelPermissions):
    """
    Ensures that the user has the appropriate
    `add`/`change`/`delete`/`view` permissions on the model.
    """

    # Map methods into required permission codes.
    # Override this if you need to also provide 'view' permissions,
    # or if you want to provide custom permission codes.
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s',
                '%(app_label)s.view_%(model_name)s_owner',
                ],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s',
                '%(app_label)s.change_%(model_name)s_owner',
                ],
        'PATCH': ['%(app_label)s.change_%(model_name)s',
                  '%(app_label)s.change_%(model_name)s_owner',
                  ],
        'DELETE': ['%(app_label)s.delete_%(model_name)s',
                   '%(app_label)s.delete_%(model_name)s_owner',
                   ],
    }

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        return [perm % kwargs for perm in self.perms_map[method]]

    def has_permission(self, request, view):

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
        else:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply DjangoModelPermissions on a view that '
            'does not set `.queryset` or have a `.get_queryset()` method.'
        )

        perms = self.get_required_permissions(request.method, queryset.model)

        # Action allowed if user has one permission on the model for that request
        for perm in perms:
            if request.user and request.user.has_perm(perm):
                return True
        return False
