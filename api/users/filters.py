import django_filters
from rest_framework import filters

from api.common.filters import (
    CommonFieldsFilterset,
    BooleanFieldFilter
)
from .models import (
    User, Group
)


class GroupFilter(CommonFieldsFilterset):
    default = BooleanFieldFilter()
    referable = BooleanFieldFilter()

    class Meta(object):
        model = Group
        fields = [
            'active', 'deleted',
            'default', 'referable'
        ]


class UserFilter(CommonFieldsFilterset):
    is_superuser = BooleanFieldFilter()
    is_admin = BooleanFieldFilter()
    # department = django_filters.CharFilter(name='department__name')
    # country = django_filters.CharFilter(name='location__country')
    # region = django_filters.CharFilter(name='location__region')
    # area = django_filters.CharFilter(name='location__area')

    class Meta(object):
        model = User
        fields = [
            'is_superuser', 'is_admin', 'email',
            # 'department', 'position',
            # 'groups','is_superuser',
            # 'country', 'region',
            # 'area', 'gender', 'email',
        ]
        order_by = [
            '-created_at',
            '-updated_at',
            'active',
            'deleted'
        ]


class UserSort(filters.OrderingFilter):

    class Meta(object):
        model = User
        fields = [
            '-last_login',
            'active', 'deleted'
        ]
