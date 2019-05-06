from django.conf.urls import url

from api.fp_growth.views import *

app_name = 'cluster'

urlpatterns = [
    url(r'^', cluster, name='cluster'),
]
