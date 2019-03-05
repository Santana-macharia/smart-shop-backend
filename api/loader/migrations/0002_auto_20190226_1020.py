# Generated by Django 2.1.5 on 2019-02-26 10:20

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='missingobservations',
            name='clean_columns',
        ),
        migrations.RemoveField(
            model_name='missingobservations',
            name='clean_data',
        ),
        migrations.RemoveField(
            model_name='missingobservations',
            name='missing_data',
        ),
        migrations.AlterField(
            model_name='distinctids',
            name='distinct_ids',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='distinctids',
            name='total_ids',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='distinctrows',
            name='distinct_rows',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='distinctrows',
            name='total_count',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='missingobservations',
            name='missing_columns',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
