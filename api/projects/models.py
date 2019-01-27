"""
Project Models
"""
import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone


class Industry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(
        default=False,
        help_text="Deletes should deactivate not do actual deletes")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return ' %s ' % self.name

    class Meta:
        app_label = 'projects'


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.CharField(max_length=254)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=40, unique=True, null=True, blank=True)
    website = models.CharField(max_length=254, null=True, blank=True)
    logo = models.CharField(max_length=254, null=True, blank=True)
    physical_address = models.TextField(null=True, blank=True)
    postal_address = models.CharField(max_length=254, null=True, blank=True)
    industry = models.ForeignKey(
        Industry, on_delete=models.CASCADE,
        null=True, blank=True, related_name='projects')
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(
        default=False,
        help_text="Deletes should deactivate not do actual deletes")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name='projects')

    def __str__(self):
        return self.company

    class Meta:
        app_label = 'projects'


from api.common.models import AbstractBase


class CustomFields(AbstractBase):
    index_field = models.CharField(max_length=60)
    index_field2 = models.CharField(max_length=60, null=True, blank=True)
    index_field3 = models.CharField(max_length=60, null=True, blank=True)
    prediction_field = models.CharField(max_length=60)
    prediction_field2 = models.CharField(max_length=60, null=True, blank=True)
    prediction_field3 = models.CharField(max_length=60, null=True, blank=True)
    date_column = models.CharField(max_length=60, null=True, blank=True)
    date_column2 =models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return 'index: %s prediction is %s' % (self.index_field, self.prediction_field)

    class Meta:
        app_label = 'projects'
