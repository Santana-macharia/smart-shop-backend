from rest_framework import serializers

from api.common.serializers import AbstractFieldsMixin
from api.loader.models import *


class DistinctRowsSerializer(AbstractFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = DistinctRows
        fields = '__all__'


class DistinctIdsSerializer(AbstractFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = DistinctIds
        fields = '__all__'


class MissingObservationsSerializer(AbstractFieldsMixin, serializers.ModelSerializer):
    missing_columns = serializers.SerializerMethodField('clean_json')

    class Meta:
        model = MissingObservations
        fields = '__all__'

    def clean_json(self, obj):
        return obj.missing_columns
