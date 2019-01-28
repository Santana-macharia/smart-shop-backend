import tablib
from django.shortcuts import render
from rest_framework import generics
from django.http import HttpResponse

from tablib import Dataset

from api.users.filters import *
from api.users.serializers import *
from api.users.resources import UserResource
from api.common.mixins import GetQuerysetMixin


class PermissionsListView(generics.ListCreateAPIView):
    """
        get:
            return list of all Permission instances
        post:
            add a new Permission instance
        """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class GroupListView(GetQuerysetMixin, generics.ListCreateAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = GroupSerializer
    filter_class = GroupFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GroupListSerializer
        return GroupSerializer


class GroupDetailView(GetQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = GroupSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GroupDetailSerializer
        return GroupSerializer


class UserCreateView(GetQuerysetMixin, generics.CreateAPIView):
    queryset = User.objects.order_by('id')
    serializer_class = UserCreateSerializer


class UserListView(GetQuerysetMixin, generics.ListAPIView):
    queryset = User.objects.order_by('id')
    serializer_class = UserListSerializer
    # filter_class = UserFilter
    search_fields = (
        'first_name', 'last_name', 'email', 'mobile',
        'department', 'position', 'employee_number',
        'status__name', 'groups__name',
        'location__country__name', 'location__region__name', 'location__area__name'
    )
    ordering = ('first_name', 'last_name', '-last_login')


class UserDetailView(GetQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailSerializer
        return UserCreateSerializer


class UserReportView(GetQuerysetMixin, generics.ListAPIView):
    queryset = User.objects.order_by('id')
    serializer_class = UserListSerializer
    filter_class = UserFilter
    search_fields = (
        'first_name', 'last_name', 'email', 'mobile',
        'department', 'position', 'employee_number',
        'status__name', 'groups__name',
        'location__country__name', 'location__region__name', 'location__area__name'
    )
    ordering = ('first_name', 'last_name', '-last_login')


def export_users_csv(request):
    dataset = UserResource().export()
    response = HttpResponse(dataset.csv, content_type='text_csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    return response


def import_users(request):
    if request.method =='POST':
        user_resource = UserResource()
        dataset = tablib.Dataset()
        user = request.user

        new_users = request.FILES['myfile']

        imported_data = dataset.load(new_users.read().decode('utf-8'))
        result = user_resource.import_data(imported_data, dry_run=True, user=user)

        if not result.has_errors():
            result = user_resource.import_data(imported_data, dry_run=False, user=user)

    return render(request, 'show_clusters.html')

