from django.shortcuts import render
from pyspark.sql.functions import col
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
    unique_fields = custom_fields(request)
    date_column = CustomFields.objects.first()
    date_column = date_column.date_column

    # First, read the data
    data_df = read_df(request,'clean')
    json_df = data_df.toPandas()
    json_df.to_json()

    # Cast all the columns to numeric
    string_columns = [date_column]
    data_df = data_df.drop(unique_fields['index'])

    new_df = data_df.select([col(c).cast("double").alias(c) for c in data_df.columns])
    # new_df.na.drop()
    new_df.printSchema()


    # Split data into training and test sets
    train, test = new_df.randomSplit([0.7, 0.3])

    # Feature Processing
    featuresCols = new_df.columns
    featuresCols.remove(unique_fields['prediction'])
    # featuresCols.remove('Temperature')
    # featuresCols.remove('Humidity')
    try:
        featuresCols.remove(date_column)
    except:
        pass
    
    # This concatenates all feature columns into a single feature vector in a new column 'rawFeatures'
    vectorAssembler = VectorAssembler(inputCols=featuresCols, outputCol='rawFeatures')
    # This identifies categorical features and indexes them
    # vectorIndexer = VectorIndexer(inputCol='rawFeatures', outputCol='features', maxCategories=4)

    # # Model Training
    # lr = LinearRegression(labelCol=unique_fields['prediction'])

    # # Model tuning
    # # paramGrid = ParamGridBuilder()\
    # #     .addGrid(gbt.maxDepth, [5, 20])\
    # #     .addGrid(gbt.maxIter, [20, 100])\
    # #     .build()
    # paramGrid = ParamGridBuilder() \
    #     .addGrid(lr.maxIter, [1, 2]) \
    #     .build()

    # # We define an evaluation metric.
    # # This tells CrossValidator how well we are doing by comparing the true labels with predictions
    # evaluator = RegressionEvaluator(metricName="rmse", labelCol=lr.getLabelCol(),
    #                                 predictionCol=lr.getPredictionCol())

    # # Declare the CrossValidator which runs model tuning for us.
    # cv = CrossValidator(estimator=lr, evaluator=evaluator, estimatorParamMaps=paramGrid)

    # # Tie the Feature Processing and model training stages into a single Pipeline
    # pipeline = Pipeline(stages=[vectorAssembler, vectorIndexer, cv])

    standardScaler = StandardScaler(inputCol="rawFeatures", outputCol="Features")
    lr = LinearRegression(maxIter=10, regParam=.01)

    stages = [vectorAssembler, standardScaler, lr]
    # Train the pipeline
    # pipelineModel = pipeline.fit(train)
    pipeline = Pipeline(stages=stages)

    model = pipeline.fit(train)
    predictions = model.transform(test)

    # # Make Predictions
    # predictions = pipelineModel.transform(test)

    # rmse = evaluator.evaluate(predictions)
    # print("RMSE on our test set is: "+str(rmse))

    predictions.show()

    predicted_df = predictions.toPandas()
    predicted_df.to_json()
    rmse = 23
    context = {
        'all_data': json_df,
        'rmse': rmse,
        'predicted': predicted_df
    }
    return render(request, 'show_predictions.html', context)