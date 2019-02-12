from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext


class Spark:
    appName = "Diseases"
    appNameSQL = "Diseases"

    conf = (SparkConf()
        .setAppName(appName)
        .set("spark.driver.host", "localhost")
        .set('spark.executor.extraClassPath',"/mnt/c/Users/Santana Macharia/Disease/Api/mysql-connector-java-5.1.40.jar")
        .set('spark.driver.extraClassPath', "/mnt/c/Users/Santana Macharia/Disease/Api/mysql-connector-java-5.1.40.jar")
        .set("spark.executor.memory", "4g")
        .set("spark.debug.maxToStringFields", "100"))

    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)