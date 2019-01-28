from django.contrib.auth.hashers import make_password
from import_export import resources
from import_export.fields import Field
from api.users.models import User


class UserResource(resources.ModelResource):

    def import_data(self, dataset, dry_run, user):
        project = user.project.id
        created_by = user.id

        dataset.append_col([created_by], header='created_by')
        dataset.append_col([project], header='project')

        return super(UserResource, self).import_data(dataset, dry_run)

    def save_instance(self, instance, using_transactions, real_dry_run):
        if not real_dry_run:
            try:
                # extra logic if object already exist
                user = User.objects.get(email=instance.email)
                pass
            except Exception:
                # create new object
                user = User(id=instance.id)

                password = instance.password
                password = make_password(password)

                created_by = self.context['request'].user
                project = self.context['request'].user.project

                user.created_by = created_by
                user.project = project
                user.password = password
                user.save()

    class Meta:
        model = User
        fields = (
            'password', 'id', 'email',
            'code', 'first_name', 'last_name',
            'mobile', 'id_number', 'dob',
            'gender', 'nationality', 'position',
            'is_admin', 'is_staff', 'groups__name',
            'project__company', 'created_by'
        )
        import_id_fields = ['id']

    def dehydrate_created_by(self, User):
        return User.created_by.get_full_name()