from django.db import models
from jsonfield import JSONField
from api.common.models import AbstractBase


class DistinctRows(AbstractBase):
    total_count = models.IntegerField(default=0, null=True, blank=True)
    distinct_rows = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return '%s total rows with %s distinct' % (str(self.total_count), str(self.distinct_rows))

    class Meta:
        app_label = 'loader'


class DistinctIds(AbstractBase):
    total_ids = models.IntegerField(default=0, null=True, blank=True)
    distinct_ids = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return '%s total ids with %s distinct' % (str(self.total_ids), str(self.distinct_ids))

    class Meta:
        app_label = 'loader'


class MissingObservations(AbstractBase):
    missing_columns = JSONField(null=True, blank=True)

    def __str__(self):
        return 'Missing observations per column %s' % (str(self.missing_columns))

    class Meta:
        app_label = 'loader'
