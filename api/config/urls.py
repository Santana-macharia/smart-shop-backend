from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, re_path
from django.conf.urls import include
from django.views.static import serve

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'auth/', include(('rest_auth.urls', 'rest_auth'), namespace='rest_auth')),
    path(r'users/', include('api.users.urls', namespace='users')),
    path(r'projects/', include('api.projects.urls', namespace='projects')),
    # path(r'loader/', include('api.loader.urls', namespace='loader')),
    # path(r'regressor/', include('api.regressor.urls', namespace='regressor')),
    # path(r'cluster/', include('api.fp_growth.urls', namespace='cluster')),
    re_path(r'^auth/obtain_token/', obtain_jwt_token),
    re_path(r'^auth/refresh_token/', refresh_jwt_token),
    path(r'browsable/', include(
        'rest_framework.urls', namespace='rest_framework')),
    re_path(r'^auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)$',
            PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^auth/password/reset/complete/$',
            PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^static/(?P<path>.*)$',
            serve, {'document_root': settings.STATIC_ROOT}),
]
