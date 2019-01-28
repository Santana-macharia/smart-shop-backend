"""
User Models
"""

import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    Group,
    AbstractBaseUser,
    PermissionsMixin
)

from api.projects.models import Project
from api.common.models import (
    AbstractBase,
    get_default_user,
    get_default_project
)


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)


class MyUserManager(BaseUserManager):
    """
    Reimplementing the django.contrib.auth.models UserManager
    by extending the BaseUserManager
    """

    # custom model to create a normal user
    def create(self, email, first_name, password=None,
               **extra_fields):
        validate_email(email)
        p = make_password(password)
        email = MyUserManager.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, password=p, **extra_fields)
        user.save(using=self._db)
        return user

    # custom model to create a super user with necessary attributes
    def create_superuser(self, email, first_name,
                         password, **extra_fields):
        user = self.create(email, first_name,
                           password, **extra_fields)
        user.active = True
        user.deleted = False
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserGroup(Group, AbstractBase):
    notes = models.TextField(blank=True)
    default = models.BooleanField(default=False)

    # custom method for group to save name and company
    def save(self, *args, **kwargs):
        if self._state.adding and self.name:
            self.name = '{} - {}'.format(self.project.company, self.name)
        super(Group, self).save(*args, **kwargs)

    def __str__(self):  # custom method for Group
        return ' %s ' % (self.name)

    class Meta:  # add extra parameters(Metadata) to Group
        ordering = ['name']


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=40, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    id_number = models.CharField(max_length=40, null=True, blank=True)
    dob = models.DateTimeField(blank=True, null=True)
    gender = models.CharField(
        max_length=20, null=True, blank=True, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=254, null=True, blank=True)
    position = models.CharField(max_length=30, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    groups = models.ManyToManyField(
        UserGroup, blank=True, related_name='users')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name='+')
    project = models.ForeignKey(
        Project, null=True, blank=True,
        on_delete=models.PROTECT, related_name='users')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self._state.adding:
            # If the user has no set created_by use the default user
            if not hasattr(self, 'created_by'):
                self.created_by = get_default_user()
            # If the user has no set project use the default project
            if not hasattr(self, 'project'):
                self.project = get_default_project()

        super(User, self).save(*args, **kwargs)

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    short_name = property(get_short_name)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (
            (self.first_name or ''), (self.last_name or ''))
        return full_name.strip()

    full_name = property(get_full_name)

    def get_permissions(self):
        """
        Returns all user permissions.
        """
        permissions = self.user_permissions.all()
        for group in self.groups.all():
            permissions = permissions | group.permissions.all()
        return permissions
    all_permissions = property(get_permissions)

    def calculate_age(self):
        """
        Returns the age of the user
        :return:
        """
        today = timezone.now()
        born = self.dob
        age = 0

        if born:
            age = today.year - born.year - \
                ((today.month, today.day) < (born.month, born.day))
        return age
    age = property(calculate_age)

    class Meta:
        app_label = 'users'
