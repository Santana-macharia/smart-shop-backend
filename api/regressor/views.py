from django.shortcuts import render
from pyspark.sql.functions import col
from django.http import JsonResponse
from pyspark.ml.feature import VectorAssembler, VectorIndexer
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import StandardScaler
from pyspark.ml import Pipeline
from pyspark.sql.functions import *

from api.common.mixins import read_df, custom_fields
from api.projects.models import CustomFields


def pipeline(request):
    company_name = request.user.project.company
    table_name = str(company_name) + '_Prediction'

    unique_fields = custom_fields(request)
    date_column = CustomFields.objects.first()
    date_column = date_column.date_column
   
    company_name = request.user.project.company
    table_name = str(company_name)+'_prediction'

    # First, read the data
    data_df = read_df(request, 'clean')
    json_df = data_df.toPandas()
    json_df.to_json()

    # Cast all the columns to numeric
    new_df = data_df.select([col(c).cast("double").alias(c) for c in data_df.columns])
    new_df = new_df.fillna(0.0)
    new_df.show()

    # Split data into training and test sets
    train, test = new_df.randomSplit([0.7, 0.3])

    # Feature Processing
    featuresCols = new_df.columns
    featuresCols.remove(unique_fields['prediction'])

    try:
        featuresCols.remove(date_column)
    except:
        pass

    # This concatenates all feature columns into a single feature vector in a new column 'rawFeatures'
    vectorAssembler = VectorAssembler(inputCols=featuresCols, outputCol='rawFeatures')

    # Model Training
    standardScaler = StandardScaler(inputCol="rawFeatures", outputCol="features")
    lr = LinearRegression(labelCol=unique_fields['prediction'], maxIter=10, regParam=.01)

    # Model tuning
    paramGrid = ParamGridBuilder() \
        .addGrid(lr.maxIter, [10, 100, 1000]) \
        .addGrid(lr.regParam, [0.1, 0.01]) \
        .addGrid(lr.fitIntercept, [False, True]) \
        .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0]) \
        .build()

    # We define an evaluation metric.
    # This tells CrossValidator how well we are doing by comparing the true labels with predictions
    evaluator = RegressionEvaluator(metricName="rmse", labelCol=lr.getLabelCol(),
                                    predictionCol=lr.getPredictionCol())

    # Declare the CrossValidator which runs model tuning for us.
    cv = CrossValidator(estimator=lr, evaluator=evaluator, estimatorParamMaps=paramGrid)

    stages = [vectorAssembler, standardScaler, cv]

    # Train the pipeline
    pipeline = Pipeline(stages=stages)
    
    model = pipeline.fit(train)
    predictions = model.transform(test)

    rmse = evaluator.evaluate(predictions)
    print("RMSE on our test set is: " + str(rmse))

    predictions.show()
    new_predictions = predictions.withColumn("rawFeatures", predictions["rawFeatures"].cast("string"))
    new_predictions = new_predictions.withColumn("features", predictions["features"].cast("string"))

    # Save predicted data to DB
    new_predictions.write.format('jdbc').options(
        url='jdbc:mysql://localhost:3306/disease',
        dbtable=table_name,
        user='santana',
        password='root').mode('append').save()

    predicted_df = predictions.toPandas()
    predicted_df.to_json()

    context = {
        'all_data': json_df,
        'rmse': rmse,
        'predicted': predicted_df
    }
    return render(request, 'show_predictions.html', context)
 
 
def predicted(request):
    show_df = read_df(request, 'prediction')
    show_df.cache()
    columns = show_df.columns

    data = show_df.take(500)

    list_data = []
    for row in data:
        row_dict = {}
        for index,item in enumerate(row):
            field = {columns[index]: item}
            row_dict.update(field)
        list_data.append(row_dict)

    result = {
        "columns": columns,
        "data": list_data
    }

    return JsonResponse(result, safe=False)
