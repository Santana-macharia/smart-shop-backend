from django.conf.urls import url

from api.users.views import *

app_name = 'users'

urlpatterns = [
    url(r'^create/$', UserCreateView.as_view(), name="users_create"),
    url(r'^create/import/$', import_users, name="import_users"),
    url(r'^permissions/$', PermissionsListView.as_view(), name="permission"),

    url(r'^groups/$', GroupListView.as_view(), name="groups_list"),
    url(r'^groups/(?P<pk>[^/]+)/$',
        GroupDetailView.as_view(), name="group_detail"),

    url(r'^departments/$', DepartmentListView.as_view(), name="departments_list"),
    url(r'^departments/reports/$', DepartmentReportView.as_view(), name="departments_reports"),
    url(r'^departments/(?P<pk>[^/]+)/$',
        DepartmentDetailView.as_view(), name="departments_detail"),

    url(r'^locations/$', UserLocationListView.as_view(), name="locations_list"),
    url(r'^locations/reports/$', UserLocationReportView.as_view(), name="locations_reports"),
    url(r'^locations/(?P<pk>[^/]+)/$',
        UserLocationDetailView.as_view(), name="locations_detail"),

    url(r'^reports/$', UserReportView.as_view(), name="users_reports"),
    url(r'^export/$', export_users_csv, name="export users into csv file"),
    url(r'^(?P<pk>[^/]+)/$', UserDetailView.as_view(), name="users_detail"),
    url(r'^', UserListView.as_view(), name="users_list"),
]
