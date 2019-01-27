import django_filters
from rest_framework import filters
from rest_framework import ISO_8601
from distutils.util import strtobool
from django.utils.encoding import force_str
from django import forms
from django.utils.dateparse import parse_datetime
from django.forms import DateTimeField

BOOLEAN_CHOICES = (
    ('false', 'False'),
    ('true', 'True'),
    ('yes', 'True'),
    ('no', 'False'),
    ('Yes', 'True'),
    ('No', 'False'),
    ('y', 'True'),
    ('n', 'False'),
    ('Y', 'True'),
    ('N', 'False'),
    ('1', 'True'),
    ('0', 'False')
)
    
DATE_INPUT_FORMATS=DateTimeField.input_formats
DATE_INPUT_FORMATS.append(ISO_8601)

class IsoDateTimeField(forms.DateTimeField):
    def strptime(self, value, format):
        value = force_str(value)
        if format == ISO_8601:
            parsed = parse_datetime(value)
            if parsed is None:  # Continue with other formats if doesn't match
                raise ValueError
            return parsed
        return super(IsoDateTimeField, self).strptime(value, format)


class IsoDateTimeFilter(django_filters.DateTimeFilter):
    """ Extend ``DateTimeFilter`` to filter by ISO 8601 formated dates too"""
    field_class = IsoDateTimeField


class ListFilterMixin(object):

    def sanitize(self, value_list):
        """
        remove empty items
        """
        return [v for v in value_list if v != u'']

    def customize(self, value):
        return value

    def filter(self, qs, value):
        multiple_vals = value.split(u",")
        multiple_vals = self.sanitize(multiple_vals)
        multiple_vals = map(self.customize, multiple_vals)
        actual_filter = django_filters.fields.Lookup(multiple_vals, 'in')
        return super(ListFilterMixin, self).filter(qs, actual_filter)


class ListCharFilter(ListFilterMixin, django_filters.CharFilter):
    """
    Enable filtering of comma separated strings.
    """
    pass


class ListIntegerFilter(ListCharFilter):
    """
    Enable filtering of comma separated integers.
    """

    def customize(self, value):
        return int(value)


class CommonFieldsFilterset(django_filters.FilterSet):
    """
        Every model that descends from AbstractBase should have this
    """
    active = django_filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES, coerce=strtobool)
    deleted = django_filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES, coerce=strtobool)

    updated_before = IsoDateTimeFilter(
        name='updated_at', lookup_expr='lte',
        input_formats=DATE_INPUT_FORMATS)
    created_before = IsoDateTimeFilter(
        name='created_at', lookup_expr='lte',
        input_formats=DATE_INPUT_FORMATS)

    updated_after = IsoDateTimeFilter(
        name='updated_at', lookup_expr='gte',
        input_formats=DATE_INPUT_FORMATS)
    created_after = IsoDateTimeFilter(
        name='created_at', lookup_expr='gte',
        input_formats=DATE_INPUT_FORMATS)

    updated_on = IsoDateTimeFilter(
        name='updated_at', lookup_expr='exact',
        input_formats=DATE_INPUT_FORMATS)
    created_on = IsoDateTimeFilter(
        name='created_at', lookup_expr='exact',
        input_formats=DATE_INPUT_FORMATS)


class BooleanFieldFilter(django_filters.Filter):
    """
    This throws a `Validation Error` if a value that is not in the
    required boolean choices is provided.
    Choices are (case insensitive):
        ['true', 't', 'yes', 'y', '1', 'false', 'f', 'no', 'n', '0]
    """
    def filter(self, qs, value):
        if value is not None:
            lc_value = value.lower()
            if lc_value in ('true', 't', 'yes', 'y', '1'):
                value = True
            elif lc_value in ('false', 'f', 'no', 'n', '0'):
                value = False
            return qs.filter(**{self.name: value})
        return qs
