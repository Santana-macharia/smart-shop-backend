from rest_framework import serializers

from api.projects.models import Project, Industry, CustomFields
from api.common.serializers import AbstractFieldsMixin


class IndustryInLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = ('id', 'name')


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class ProjectInLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'company')


class ProjectListSerializer(serializers.ModelSerializer):
    industry = IndustryInLineSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class IndustrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = '__all__'


class CustomFieldsSerializer(AbstractFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = CustomFields
        fields = '__all__'
