from django.conf.urls import url
from api.loader.views import *

app_name = 'loader'

urlpatterns = [
    url(r'^upload/$', import_data, name="import_data"),
    # url(r'^distinct_rows/$', show_distinct_rows, name="distinct_rows"),
    # url(r'^distinct_ids/$', show_distinct_ids, name="distinct_ids"),
    # url(r'^missing_observations/$', show_missing_observations, name="missing_observations"),

    url(r'^pre_process/$', pre_process, name="full_pre_processing"),
    url(r'^clean_data/$', clean_data, name="cleaned_data"),
    url(r'^rows/$', DistinctRowsList.as_view(), name='list_rows'),
    url(r'^ids/$', DistinctIdsList.as_view(), name='list_ids'),
    url(r'^missing/$', MissingObservationsList.as_view(), name='show_missing'),
]