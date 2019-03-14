from django.conf.urls import url
from api.regressor.views import *

app_name = 'regressor'

urlpatterns = [
    url(r'^', pipeline, name="pipeline"),
#     url(r'^distinct_rows/$', show_distinct_rows, name="distinct_rows"),
#     url(r'^distinct_ids/$', show_distinct_ids, name="distinct_ids"),
#     url(r'^missing_observations/$', show_missing_observations, name="missing_observations"),
#     url(r'^pre_process/$', pre_process, name="full_pre_processing"),
]