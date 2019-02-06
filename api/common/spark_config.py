from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext


class Spark:
    appName = "Diseases"
    appNameSQL = "Diseases"

    conf = (SparkConf()
        .setAppName(appName)
        .set("spark.driver.host", "localhost")
        .set('spark.executor.extraClassPath',"/mnt/c/Users/User/Bisda/Bisda_Api/mysql-connector-java-5.1.40.jar")
        .set('spark.driver.extraClassPath', "/mnt/c/Users/User/Bisda/Bisda_Api/mysql-connector-java-5.1.40.jar")
        .set("spark.executor.memory", "4g"))

    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)