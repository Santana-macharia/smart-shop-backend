import django_filters

from api.common.filters import (
    CommonFieldsFilterset
)
from api.projects.models import Project, Industry


class ProjectFilter(CommonFieldsFilterset):
    industry = django_filters.CharFilter(name='industry__name')

    class Meta:
        model = Project
        fields = [
            'company', 'email',
            'website', 'industry'
        ]
        order_by = [
            '-created_at',
            '-updated_at',
            'active',
            'deleted'
        ]


class IndustryFilter(CommonFieldsFilterset):

    class Meta:
        model = Industry
        fields = ['name']
        order_by = [
            '-created_at',
            '-updated_at',
            'active',
            'deleted'
        ]