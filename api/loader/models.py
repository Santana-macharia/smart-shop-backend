from django.db import models

from api.common.models import AbstractBase


class DistinctRows(AbstractBase):
    total_count = models.IntegerField(default=0)
    distinct_rows = models.IntegerField(default=0)

    def __str__(self):
        return '%s total rows with %s distinct' % (str(self.total_count), str(self.distinct_rows))

    class Meta:
        app_label = 'loader'


class DistinctIds(AbstractBase):
    total_ids = models.IntegerField(default=0)
    distinct_ids = models.IntegerField(default=0)

    def __str__(self):
        return '%s total ids with %s distinct' % (str(self.total_ids), str(self.distinct_ids))

    class Meta:
        app_label = 'loader'


class MissingObservations(AbstractBase):
    missing_columns = models.TextField(blank=True, null=True)
    missing_data = models.TextField(blank=True, null=True)
    clean_columns = models.TextField(blank=True, null=True)
    clean_data = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'loader'