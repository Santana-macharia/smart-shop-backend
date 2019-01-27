from django.conf.urls import url

from api.projects.views import *

app_name = 'projects'

urlpatterns = [
    url(r'^industry/$', IndustryListView.as_view(), name='industries'),
    url(r'^industry/reports/$', IndustryReportView.as_view(), name='industries_reports'),
    url(r'^industry/(?P<pk>[^/]+)/$', IndustryDetailView.as_view(),
        name='industries'),
    url(r'^reports/$', ProjectReportView.as_view(),
        name='project_reports'),
    url(r'^custom_fields/$', CustomFieldsView.as_view(), name='custom_fields'),
    url(r'^custom_fields/(?P<pk>[^/]+)/$', CustomFieldDetailView.as_view(), name='custom_field_detail'),
    url(r'^(?P<pk>[^/]+)/$', ProjectDetailView.as_view(),
        name='project_detail'),
    url(r'^', ProjectListCreateView.as_view(), name='projects'),
]
