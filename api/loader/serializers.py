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

    class Meta:
        model = MissingObservations
        fields = '__all__'