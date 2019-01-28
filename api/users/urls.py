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

    url(r'^reports/$', UserReportView.as_view(), name="users_reports"),
    url(r'^export/$', export_users_csv, name="export users into csv file"),
    url(r'^(?P<pk>[^/]+)/$', UserDetailView.as_view(), name="users_detail"),
    url(r'^', UserListView.as_view(), name="users_list"),
]
