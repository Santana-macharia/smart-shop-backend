from rest_framework import generics

from api.common.mixins import GetQuerysetMixin
from api.projects.serializers import *
from api.projects.filters import ProjectFilter,IndustryFilter


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.order_by('id')
    serializer_class = ProjectSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer


class ProjectReportView(generics.ListAPIView):
    queryset = Project.objects.order_by('id')
    serializer_class = ProjectSerializer
    filter_class = ProjectFilter


class IndustryListView(generics.ListCreateAPIView):
    queryset = Industry.objects.order_by('id')
    serializer_class = IndustrySerializer


class IndustryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


class IndustryReportView(generics.ListAPIView):
    queryset = Industry.objects.order_by('id')
    serializer_class = IndustrySerializer
    filter_class = IndustryFilter


class CustomFieldsView(GetQuerysetMixin, generics.ListCreateAPIView):
    queryset = CustomFields.objects.order_by('id')
    serializer_class = CustomFieldsSerializer


class CustomFieldDetailView(GetQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomFields.objects.order_by('id')
    serializer_class = CustomFieldsSerializer
