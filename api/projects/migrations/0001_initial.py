# Generated by Django 2.1.5 on 2019-01-28 14:13

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFields',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False, help_text='Deletes should deactivate not do actual deletes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('index_field', models.CharField(max_length=60)),
                ('index_field2', models.CharField(blank=True, max_length=60, null=True)),
                ('index_field3', models.CharField(blank=True, max_length=60, null=True)),
                ('prediction_field', models.CharField(max_length=60)),
                ('prediction_field2', models.CharField(blank=True, max_length=60, null=True)),
                ('prediction_field3', models.CharField(blank=True, max_length=60, null=True)),
                ('date_column', models.CharField(blank=True, max_length=60, null=True)),
                ('date_column2', models.CharField(blank=True, max_length=60, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=254)),
                ('description', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False, help_text='Deletes should deactivate not do actual deletes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('company', models.CharField(max_length=254)),
                ('phone_number', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(blank=True, max_length=40, null=True, unique=True)),
                ('website', models.CharField(blank=True, max_length=254, null=True)),
                ('logo', models.CharField(blank=True, max_length=254, null=True)),
                ('physical_address', models.TextField(blank=True, null=True)),
                ('postal_address', models.CharField(blank=True, max_length=254, null=True)),
                ('active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False, help_text='Deletes should deactivate not do actual deletes')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
