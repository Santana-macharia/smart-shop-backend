"""
User serializers
"""

from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers, ISO_8601
from django.forms import DateTimeField
from rest_framework.validators import UniqueTogetherValidator

from rest_auth.serializers import (
    TokenSerializer,
    PasswordResetSerializer
)
from api.common.serializers import (
    AbstractFieldsMixin,
)
from api.projects.serializers import ProjectInLineSerializer

from api.users.models import *
from rest_framework.authtoken.models import Token


DATE_INPUT_FORMATS = DateTimeField.input_formats
DATE_INPUT_FORMATS.append(ISO_8601)


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type')


class PermissionInlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')


class GroupInlineSerializer(AbstractFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = UserGroup
        fields = ('id', 'name')


class GroupSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])

        group = super(GroupSerializer, self).create(validated_data)

        if permissions:
            group.permissions.add(*permissions)

        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if permissions:
            instance.permissions.clear()
            instance.permissions.add(*permissions)

        return instance

    class Meta(object):
        model = UserGroup
        fields = '__all__'


class GroupListSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    permissions = PermissionInlineSerializer(many=True)

    class Meta:
        model = UserGroup
        exclude = ('permissions',)
        # Ensure there is only one default group per project
        validators = [
            UniqueTogetherValidator(
                queryset=UserGroup.objects.filter(default=True),
                fields=('project', 'default'),
                message='There can only be one default group'
            )
        ]


class GroupDetailSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    permissions = PermissionInlineSerializer(many=True)

    class Meta:
        model = UserGroup
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField(source='calculate_age')

    @transaction.atomic
    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        # password = validated_data.pop('password', None)
        user_permissions = validated_data.pop('user_permissions', [])

        validated_data['updated_at'] = timezone.now()
        validated_data['active'] = True
        validated_data['deleted'] = False

        # validated_data['password'] = make_password(password)

        if not validated_data.get('created_by', None):
            validated_data['created_by'] = self.context['request'].user

        if not validated_data.get('created_at', None):
            validated_data['created_at'] = timezone.now()

        new_user = super(UserCreateSerializer, self).create(validated_data)
        new_user.groups.add(*groups)
        new_user.user_permissions.add(*user_permissions)

        return new_user

    @transaction.atomic
    def update(self, user, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        user_permissions = validated_data.pop('user_permissions', [])

        for attr, value in validated_data.items():
            setattr(user, attr, value)

        # In case update contains  a password
        if password is not None:
            # password = make_password(password)
            setattr(user, 'password', password)

        user.updated_at = timezone.now()
        user.save()

        if groups:
            user.groups.clear()
            user.groups.add(*groups)

        if user_permissions:
            user.user_permissions.clear()
            user.user_permissions.add(*user_permissions)

        return user

    class Meta:
        model = User
        fields = '__all__'


class UserListSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')
    short_name = serializers.ReadOnlyField(source='get_short_name')
    age = serializers.ReadOnlyField(source='calculate_age')
    project = ProjectInLineSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ('password', 'user_permissions', 'dob')


class UserDetailSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')
    short_name = serializers.ReadOnlyField(source='get_short_name')
    age = serializers.ReadOnlyField(source='calculate_age')
    project = ProjectInLineSerializer(read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class UserInLineSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile')


class UserAuthTokenSerializer(TokenSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user')


# Overrides Django rest-auth PasswordResetSerializer
class UserPasswordResetSerializer(PasswordResetSerializer):
    email = serializers.EmailField()

    """Override this method to change default e-mail options"""

    def get_email_options(self):
        request = self.context.get('request')

        # Temporary solution for mobile app
        if 'HTTP_ORIGIN' in request.META:
            domain = request.META['HTTP_ORIGIN']
        else:
            domain = getattr(settings, 'CLIENT_ORIGIN')

        return {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'domain_override': domain,
            'html_email_template_name': 'users/password_reset/password_reset_email.html'
        }

    def validate_email(self, email):
        # Check if user exists
        # Check user submits own email
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                {'user': ["{} does not exist".format(email)]})

        return super(UserPasswordResetSerializer, self).validate_email(email)
