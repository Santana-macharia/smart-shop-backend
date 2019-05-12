from django.shortcuts import render
from pyspark.ml.fpm import FPGrowth
from pyspark.sql.functions import col, collect_list
from pyspark.ml.feature import VectorAssembler, VectorIndexer
from pyspark.sql import  types as typ

from api.common.mixins import read_df, custom_fields
from api.common.spark_config import Spark
from pyspark.ml.feature import CountVectorizer

def cluster(request):
    unique_fields = custom_fields(request)
    # First, read the data
    data_df = read_df(request, 'clean')
    data_df.cache()
    json_df = data_df.toPandas()
    json_df.to_json()

    #transformer df to rdd
    #td = data_df.rdd 

    

    # Create a tuple of id and items from the Data Frame
    dd = []
    for p in data_df:
        dd.append(p)

    data = []
    for row in json_df.itertuples():
        id = row[1]
        items = []

        for column in range(2, (len(dd)+1)):
            items.append(row[column])
        data.append((id, items))

    # Create a Data Frame from the data dictionary
    final_data = Spark.sqlContext.createDataFrame(data, ["id", "items"])
    

    # Create the FPGrowth instance with its arguments and train the model
    fpGrowth = FPGrowth(itemsCol='items', minSupport=0.5, minConfidence=0.6)
    model = fpGrowth.fit(final_data)

    # Frequent Item sets
    itemSets = model.freqItemsets

    # Generated Association Rules
    assocRules = model.associationRules

    # Examines input items against all association rules and summarize consequents as prediction
<<<<<<< HEAD
    prediction = model.transform(final_data)

   
=======
    prediction = model.transform(data)

>>>>>>> b1556b7eb63d5ebe67b661f2432420a4e9881dc8
    context = {
        'all_data': json_df,
        'itemSets': itemSets,
        'assocRules': assocRules,
        'predicted': prediction
    }
    return render(request, 'show_clusters.html', context)