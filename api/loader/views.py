import json
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from django.utils import timezone
import datetime
from datetime import datetime as dt
from pyspark.sql import functions as fn, types as typ
from pyspark.sql.functions import col

from api.common.mixins import read_df, custom_fields, GetQuerysetMixin
from api.common.spark_config import Spark
from api.loader.models import *
from api.loader.serializers import *
from api.projects.models import CustomFields


def import_data(request):
    if request.method =='POST':
        new_file = next(iter(request.FILES.values()))
        # new_file = request.FILES['myfile']
        path = 'data/'+ str(new_file.name)
        project_id = request.user.project.id
        company_name = request.user.project.company

        data = Spark.sc.textFile(path)
        header = data.first()


        # fields2 = [(typ.StructField(h, typ.DateType(), True)) for h in header.split(',') if ('Date' in str(h) else (typ.StructField(h, typ.StringType(), True))
        #           for h in header.split(',')]

        # fields1 = [typ.StructField(h, typ.StringType(), True)
        #           for h in header.split(',')]
        fields = []
        date_column = None
        drop_column = None
        for index, field_name in enumerate(header.split(',')):
            if ('Date' in str(field_name)):
                date_column = index
                drop_column = field_name
                fields.append(typ.StructField(field_name, typ.DateType(), True))
            else:
                fields.append(typ.StructField(field_name, typ.StringType(), True))
        schema = typ.StructType(fields)

        data = data.filter(lambda row: row != header) \
            .map(lambda row: [dt.strptime(elem, '%d/%m/%Y') if (index==date_column) else str(elem) for index, elem in enumerate(row.split(','))])

        data_df = Spark.sqlContext.createDataFrame(data, schema)
        table_name = str(company_name)+'_Test'
        data_df.drop(drop_column).collect()

        unique_value = CustomFields.objects.get(project_id=project_id)
        unique_value.date_column = date_column
        unique_value.save()

        data_df.write.format('jdbc').options(
            url='jdbc:mysql://localhost:3306/bisda',
            dbtable=table_name,
            user='b_d',
            password='b_d_password').mode('append').save()

    return render(request, 'import_users.html')


def show_distinct_rows(request):
    # First, read the data
    data_df = read_df(request, 'test')
    json_df = data_df.toPandas()
    json_df.to_json()

    # Second, check the data for duplicate rows
    distinct_df = data_df.distinct()  # Get the total number of distinct records

    # Remove any duplicates if they exist
    if data_df.count() != distinct_df.count():
        non_duplicates_df = data_df.dropDuplicates()
    else:
        non_duplicates_df = data_df

    model_data = DistinctRows.objects.create(total_count=data_df.count(), distinct_rows=distinct_df.count())
    model_data.save()

    context = {'all_data': json_df, 'count': data_df.count(),
               'distinct_count': distinct_df.count(), 'distinct_df': non_duplicates_df}
    return render(request, 'show_distinct.html', context)


def show_distinct_ids(request):
    # Read all the custom fields
    unique_fields = custom_fields(request)

    # First, read the data
    data_df = read_df(request, 'test')
    json_df = data_df.toPandas()
    json_df.to_json()

    # Second, check data for duplicates despite the ID attribute
    distinct_rows = data_df.select([
        c for c in data_df.columns if c != unique_fields['index']
    ]).distinct()

    # Drop rows that are similar but may have different ids
    if data_df.count() != distinct_rows.count():
        unique_rows_df = data_df.dropDuplicates(subset=[
            c for c in data_df.columns if c != unique_fields['index']
        ])
    else:
        unique_rows_df = data_df

    # Count the number of distinct id fields
    distinct_ids = unique_rows_df.agg(
        fn.countDistinct(unique_fields['index']).alias('distinct')
    )
    ids = distinct_ids.select('distinct').collect()
    distinct = ids[0].distinct

    # This means there are rows with same id(s) but are not duplicates
    if unique_rows_df.count() != distinct:
        clean_df = unique_rows_df.withColumn('New_id',
                                    fn.monotonically_increasing_id())
    else:
        clean_df = unique_rows_df

    clean_json = clean_df.toPandas()
    clean_json.to_json()

    model_data = DistinctIds.objects.create(total_ids=data_df.count(), distinct_ids=distinct)
    model_data.save()

    context = {'all_data': json_df, 'distinct_ids': distinct,
               'clean_df': clean_json}
    return render(request, 'show_distinct.html', context)


def show_missing_observations(request):
    # Read all the custom fields
    unique_fields = custom_fields(request)

    # First, read the data
    data_df = read_df(request, 'test')
    json_df = data_df.toPandas()
    json_df.to_json()

    # Get the Date column
    date_column = None
    for col in data_df.columns:
        if ('Date' in str(col)):
            date_column = col

    # Show the number of missing observations per row as a percentage
    df_percentage = data_df.agg(*[
            (1 - (fn.count(c) / fn.count('*'))).alias(c + '_missing')
            for c in data_df.columns
        ]).collect()
    df_percentage = df_percentage[0]

    # Drop the rows whose missing observations exceed a certain threshold
    data_less_rows = data_df.dropna(thresh=3)

    # Calculate the mean for every non boolean field
    means = data_less_rows.agg(
        *[fn.mean(c).alias(c)
          for c in data_less_rows.columns if c != date_column]
    ).toPandas().to_dict('records')[0]

    means[date_column] = 'missing'
    for key, value in means.items():
        if (means[key] == None):
            means[key] = 'missing'

    # Fill the empty observations with the mean of the column
    data_less_rows.fillna(means)

    clean_json_df = data_less_rows.toPandas()
    clean_json_df.to_json()

    columns = data_less_rows.columns
    data = []

    for item in df_percentage:
        data.append(item)

    columns_json = json.dumps(columns)
    data_json = json.dumps(data)

    model_data = MissingObservations.objects.create(missing_columns=columns_json, missing_data=data_json)
    model_data.save()

    context = {'all_data': json_df, 'missing_percentages': df_percentage,
               'clean_data': clean_json_df}
    return render(request, 'show_distinct.html', context)


def pre_process(request):
    # Read all the custom fields
    unique_fields = custom_fields(request)
    company_name = request.user.project.company

    # First, read the data
    data_df = read_df(request, 'test')
    json_df = data_df.toPandas()
    json_df.to_json()

    # Get the Date column
    date_column = None
    for col in data_df.columns:
        if('Date' in str(col)):
            date_column = col

# Second, check the data for duplicate rows
    distinct_df = data_df.distinct()    # Get the total number of distinct records

    # Remove any duplicates if they exist
    if data_df.count() != distinct_df.count():
        non_duplicates_df = data_df.dropDuplicates()
    else:
        non_duplicates_df = data_df

    # Third, check data for duplicates despite the ID attribute
    distinct_rows = non_duplicates_df.select([
        c for c in non_duplicates_df.columns if c != unique_fields['index']
    ]).distinct()

    # Drop rows that are similar but may have different ids
    if non_duplicates_df.count() != distinct_rows.count():
        unique_rows_df = non_duplicates_df.dropDuplicates(subset=[
            c for c in non_duplicates_df.columns if c != unique_fields['index']
        ])
    else:
        unique_rows_df = non_duplicates_df

    # Count the number of distinct id fields
    distinct_ids = unique_rows_df.agg(
        fn.countDistinct(unique_fields['index']).alias('distinct')
    )
    ids = distinct_ids.select('distinct').collect()
    distinct = ids[0].distinct

    # This means there are rows with same id(s) but are not duplicates
    if unique_rows_df.count() != distinct:
        clean_df = unique_rows_df.withColumn('New_id',
                                     fn.monotonically_increasing_id())
    else:
        clean_df = unique_rows_df

    # Show the number of missing observations per row as a percentage
    df_percentage = clean_df.agg(*[
        (1- (fn.count(c) / fn.count('*'))).alias(c + '_missing')
        for c in clean_df.columns
    ]).collect()

    # Can instead use correlation to check which attributes to drop

    # Drop the rows whose missing observations exceed a certain threshold
    data_less_rows = clean_df.dropna(thresh=3)

    # Calculate the mean for every non boolean field
    means = data_less_rows.agg(
        *[fn.mean(c).alias(c)
          for c in data_less_rows.columns if c!=date_column]
    ).toPandas().to_dict('records')[0]

    means[date_column] = 'missing'
    for key, value in means.items():
        if (means[key]==None):
            means[key] = 'missing'

    # Fill the empty observations with the mean of the column
    data_less_rows.fillna(means)

    clean_json_df = data_less_rows.toPandas()
    clean_json_df.to_json()

    table_name = str(company_name) + '_Clean'

    # Final step is to save the pre_processed DF to the DB
    data_less_rows.write.format('jdbc').options(
        url='jdbc:mysql://localhost:3306/bisda',
        dbtable=table_name,
        user='b_d',
        password='b_d_password').mode('append').save()

    context = {
                'all_data': json_df,
                'rows_count': data_df.count,
                'distinct_rows': distinct_rows.count,
                'distinct_rows_without_id': distinct_rows.count,
                'distinct_ids': distinct,
                'missing_percentages': df_percentage,
                'clean_data': clean_json_df
    }
    return render(request, 'show_distinct.html', context)

# def ListMissingObservations(request):
#     # First, read the data
#     # data_df = read_df(request, 'clean')
#     data_df = Spark.sqlContext.read.format('jdbc') \
#         .options(
#         url='jdbc:mysql://localhost:3306/bisda',
#         dbtable='Swisscom_Clean',
#         # dbtable=(str(name+'Data')),
#         useSSL=False,
#         user='b_d',
#         password='b_d_password').load()
#
#     json_df = data_df.toPandas()
#     json_df.to_json()
#
#     columns = data_df.columns
#
#     rdd = data_df.rdd.map(list)
#     data = rdd.collect()
#
#     context = {'columns': columns, 'rows': data}
#     return (context)


class MissingObservationsList(GetQuerysetMixin, generics.ListAPIView):
    queryset = MissingObservations.objects.order_by('id')
    serializer_class = MissingObservationsSerializer


class DistinctRowsList(GetQuerysetMixin, generics.ListAPIView):
    queryset = DistinctRows.objects.order_by('id')
    serializer_class = DistinctRowsSerializer


class DistinctIdsList(GetQuerysetMixin, generics.ListAPIView):
    queryset = DistinctIds.objects.order_by('id')
    serializer_class =DistinctIdsSerializer

class MissingObservationsList(GetQuerysetMixin, generics.ListAPIView):
    queryset = MissingObservations.objects.order_by('id')
    serializer_class = MissingObservationsSerializer