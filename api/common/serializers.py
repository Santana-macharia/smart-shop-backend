import datetime
import calendar

from django.db import transaction
from django.utils import timezone


def get_month_range(date=timezone.now()):
    """
    For a date 'date' returns the start and end date for the month of 'date'.

    Month with 31 days:
    >>> date = datetime.date(2011, 7, 27)
    >>> get_month_day_range(date)
    (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))

    Month with 28 days:
    >>> date = datetime.date(2011, 2, 15)
    >>> get_month_day_range(date)
    (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
    """
    first_day = date.replace(day=1)
    last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day, last_day


def generate_days(start_date, end_date):
    """
    Generator creates list of days between start_date and end_date
    :param start_date: The beginning of the date generation
    :param end_date: The last day in the generation
    :return:
    """
    current_day = start_date
    while current_day <= end_date:
        yield current_day
        current_day += datetime.timedelta(days=1)


class AbstractFieldsMixin(object):
    """
    Injects the fields in the abstract base model as a model
    instance is being saved.
    """

    def __init__(self, *args, **kwargs):
        super(AbstractFieldsMixin, self).__init__(*args, **kwargs)

    @transaction.atomic
    def create(self, validated_data):
        """`created` and `created_by` are only mutated if they are null"""
        if not validated_data.get('created_at', None):
            validated_data['created_at'] = timezone.now()

        validated_data['updated_at'] = timezone.now()
        validated_data['active'] = True
        validated_data['deleted'] = False

        if not validated_data.get('created_by', None):
            validated_data['created_by'] = self.context['request'].user

        if not validated_data.get('project', None):
            validated_data['project'] = self.context['request'].user.project

        return self.Meta.model.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        # cannot update obj's project once set
        self.validated_data.pop('project', None)

        # Make  sure the updated_at field is set to current time
        validated_data['updated_at'] = timezone.now()

        return super(AbstractFieldsMixin, self).update(instance, validated_data)

    class Meta:
        exclude = (
            'deleted', 'active',
            'created_at', 'updated_at',
            'created_by', 'project'
        )
