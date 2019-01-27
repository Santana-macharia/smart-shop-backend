"""
Common Models
"""

import uuid
import logging

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

from api.projects.models import Project

LOGGER = logging.getLogger(__file__)


def get_default_user():
    """
    Ensure that there is a default system user
    """
    try:
        return get_user_model().objects.get(
            email='santanamash@gmail.com'
        )
    except get_user_model().DoesNotExist:
        return get_user_model().objects.create(
            email='santanamash@gmail.com',
            first_name='Santana',
            last_name='Macharia',
            password='macharia',
            last_login=timezone.now(),
            project=get_default_project()
        )


def get_default_user_id():
    """
    Get the default system user's id
    """
    return get_default_user().pk


def get_default_project():
    """
    Ensure that there is a default system project
    """
    try:
        return Project.objects.get(
            email='santanamash@gmail.com'
        )
    except Project.DoesNotExist:
        return Project.objects.create(
            email='santanamash@gmail.com',
            company='Santana Macharia'
        )


def get_default_project_id():
    """
    Get the default system project id
    """
    return get_default_project().pk


class AbstractBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(
        default=False,
        help_text="Deletes should deactivate not do actual deletes")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True,
        on_delete=models.PROTECT, related_name='+')
    project = models.ForeignKey(
        Project, blank=True,
        on_delete=models.PROTECT, related_name='+')

    def preserve_created_and_created_by(self):
        """
        Ensures that in subsequent times created and created_by fields
        values are not overridden.
        """
        try:
            original = self.__class__.objects.get(pk=self.pk)
            self.created_at = original.created_at
            self.created_by = original.created_by
        except self.__class__.DoesNotExist:
            LOGGER.info(
                'preserve_created_and_created_by '
                'Could not find an instance of {} with pk {} hence treating '
                'this as a new record.'.format(self.__class__, self.pk))

    def save(self, *args, **kwargs):
        if self._state.adding:
            # If the user has no set created_by use the default user
            if not hasattr(self, 'created_by'):
                self.created_by = get_default_user()
            # If the user has no set project use the default project
            if not hasattr(self, 'project'):
                self.project = get_default_project()

        self.full_clean(exclude=None)
        self.preserve_created_and_created_by()

        super(AbstractBase, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Mark the field model deleted
        self.deleted = True
        self.save()

    class Meta:
        abstract = True
        ordering = ('-updated_at', 'created_at')


class AltAbstractBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(
        default=False,
        help_text="Deletes should deactivate not do actual deletes")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True,
        on_delete=models.PROTECT, related_name='+')

    def preserve_created_and_created_by(self):
        """
        Ensures that in subsequent times created and created_by fields
        values are not overridden.
        """
        try:
            original = self.__class__.objects.get(pk=self.pk)
            self.created_at = original.created_at
            self.created_by = original.created_by
        except self.__class__.DoesNotExist:
            LOGGER.info(
                'preserve_created_and_created_by '
                'Could not find an instance of {} with pk {} hence treating '
                'this as a new record.'.format(self.__class__, self.pk))

    def save(self, *args, **kwargs):
        if self._state.adding:
            # If the user has no set created_by use the default user
            if not hasattr(self, 'created_by'):
                self.created_by = get_default_user()

        self.full_clean(exclude=None)
        self.preserve_created_and_created_by()

        super(AltAbstractBase, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Mark the field model deleted
        self.deleted = True
        self.save()

    class Meta:
        abstract = True
        ordering = ('-updated_at', 'created_at')
