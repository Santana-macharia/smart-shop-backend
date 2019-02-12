from import_export import resources
from api.users.models import User


class LoadResource(resources.ModelResource):

    def import_data(self, dataset, dry_run, user):
        project = user.project.id
        created_by = user.id

        dataset.append_col([created_by], header='created_by')
        dataset.append_col([project], header='project')

        return (super(LoadResource, self).import_data(dataset, dry_run))


    def save_instance(self, instance, using_transactions, real_dry_run):
        if not real_dry_run:
            try:
                # extra logic if object already exist
                user = User.objects.get(email=instance.email)
                pass
            except Exception:
                # create new object
                pass

    class Meta:
        model = User
        fields = (
            'password', 'id', 'email',
            'code', 'first_name', 'last_name',
            'mobile', 'id_number', 'dob',
            'gender', 'nationality', 'position',
            'is_admin', 'is_staff', 'groups__name',
            'department__name', 'location',
        )
        import_id_fields = ['id']

    def dehydrate_created_by(self, User):
        return User.created_by.get_full_name()