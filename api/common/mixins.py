"""
    Helps provide more functionality to views
"""
import operator
from functools import reduce
from django.db.models import Q

from api.common.permissions import DjangoModifiedModelPermissions
from api.common.models import get_default_project
from api.common.spark_config import Spark
from api.projects.models import CustomFields


def read_df(self, db_type):
    project = self.user.project.company
    if db_type is 'clean':
        name = 'Clean'
    else:
        name = 'Test'
    table_name = str(project)+'_'+name
    data_df = Spark.sqlContext.read.format('jdbc') \
        .options(
        url='jdbc:mysql://localhost:3306/disease',
        dbtable=table_name,
        # dbtable=(str(name+'Data')),
        useSSL=False,
        user='santana',
        password='root').load()
    return data_df


def custom_fields(self):
    custom_fields = CustomFields.objects.first()

    if custom_fields.index_field2 != '' or custom_fields.index_field3 != '':
        index_field = []
        if custom_fields.index_field2 != '':
            index_field.append(custom_fields.index_field2)
        if custom_fields.index_field3 != '':
            index_field.append(custom_fields.index_field3)

    else:
        index_field = custom_fields.index_field

    if custom_fields.prediction_field2 != '' or custom_fields.prediction_field3 != '':
        prediction_field = []
        if custom_fields.prediction_field2 != '':
            prediction_field.append(custom_fields.prediction_field2)
        if custom_fields.prediction_field3 != '':
            prediction_field.append(custom_fields.prediction_field3)

    else:
        prediction_field = custom_fields.prediction_field

    new_fields = {
        'index': index_field,
        'prediction': prediction_field
    }
    return new_fields


class GetProjectMixin(object):
    project = None

    def get_project(self):
        """
            Tries to get the project of a given object
        """
        if not self.project:
            model = self.serializer_class.Meta.model

            object_id = self.kwargs.get('pk', None)
            # try to retrieve project for the object
            if object_id:
                if not hasattr(model, 'project'):
                    return model.objects.get(pk=object_id)
                try:
                    self.project = model.objects.get(pk=object_id).project
                except model.DoesNotExist:
                    pass
            # try to get current user's project
            if not self.project and self.request.user.is_authenticated:
                self.project = self.request.user.project
            # Temporary solution for non-project users
            if not self.project:
                self.project = get_default_project()

        return self.project


class GetQuerysetMixin(GetProjectMixin):
    """
        Ensure only logged in user's project data is retrieved
    """

    # Convert string to bool
    def strtobool(self, value):
        return value.lower() in ("yes", "true", "t", "1")

    def get_queryset(self, *args, **kwargs):
        queryset = super(GetQuerysetMixin, self).get_queryset(*args, **kwargs)
        queryset = queryset.filter(project=self.get_project())

        user = self.request.user
        model = self.serializer_class.Meta.model
        model_name = model.__name__.lower()
        method = self.request.method

        permission_class = DjangoModifiedModelPermissions()
        required_perms = permission_class.get_required_permissions(
            method, model)

        perm = required_perms[0]
        perm_owner = required_perms[1]

        if method == 'GET':
            # If listing, otherwise its a retrieval
            # List only active and undeleted items
            # This is a hack (Better implementation needed)
            if callable(getattr(self, 'list', None)):
                active = self.strtobool(
                    self.request.query_params.get('active', 'True'))
                deleted = self.strtobool(
                    self.request.query_params.get('deleted', 'False'))
                queryset = queryset.filter(active=active, deleted=deleted)

            # perm_all is unecessary since perm already exists and returns same
            # set of permissions
            if user.has_perm(perm) or user.is_superuser:
                self.queryset = queryset

            elif user.has_perm(perm_owner):
                if hasattr(model, 'created_by'):
                    if hasattr(model, 'user'):
                        self.queryset = queryset.filter(
                            created_by=user) | queryset.filter(
                            user=user
                        )
                    elif hasattr(model, 'owners'):
                        self.queryset = queryset.filter(
                            created_by=user) | queryset.filter(
                            owners=user
                        )
                    else:
                        self.queryset = queryset.filter(created_by=user)
                else:
                    self.queryset = queryset.none()

            else:
                self.queryset = queryset.none()

            query = self.request.GET.get("q") or False
            # An icontains search using values in search fields specified in the
            # calling view
            if query and hasattr(self, 'search_fields'):
                fields = [(field + '__icontains', query)
                          for field in self.search_fields]

                q_list = [Q(x) for x in fields]

                self.queryset = self.queryset.filter(
                    reduce(operator.or_, q_list)
                )

                self.queryset = self.queryset.distinct()

        # Checks to see that logged in user has permission to update data
        if method == 'PATCH' or method == 'PUT':
            # Checks to see if user has been granted all permissions
            if user.has_perm(perm) or user.is_superuser:
                pass
            # Checks to see if user is owner of the object
            elif user.has_perm(perm_owner):
                if not self.request.data:
                    pass
                elif hasattr(model, 'created_by') and self.get_object().created_by == user:
                    pass
                elif hasattr(model, 'owners') and user in self.get_object().owners:
                    pass
                elif hasattr(model, 'user') and self.get_object().user == user:
                    pass
                else:
                    self.permission_denied(
                        self.request,
                        message="You have no permission to change this %s object" % model_name
                    )

            else:
                self.permission_denied(
                    self.request,
                    message="You have no permission to change this %s object" % model_name
                )
        # Checks to  see that logged in user has permission to delete the object
        elif method == 'DELETE':
            # Checks to see if user has been granted all permissions
            if user.has_perm(perm) or user.is_superuser:
                pass

            # Checks to see if user is owner of the object
            elif user.has_perm(perm_owner):
                if not self.request.data:
                    pass
                elif hasattr(model, 'created_by') and self.get_object() == user:
                    pass
                elif hasattr(model, 'owners') and user in self.request.data['owners']:
                    pass
                elif hasattr(model, 'user') and self.request.data['user'] == user.id:
                    pass
                else:
                    self.permission_denied(
                        self.request,
                        message="You have no permission to delete this %s object" % model_name
                    )

            else:
                self.permission_denied(
                    self.request,
                    message="You have no permission to delete this %s" % model_name
                )
        else:
            pass

        return self.queryset
