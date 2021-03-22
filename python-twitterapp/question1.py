from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
import os
DATA_PATH = '../data/French/'
files = os.listdir(DATA_PATH)
files_path = [DATA_PATH+f for f in files]
# print(files)
# spark = SparkSession.builder.getOrCreate()
conf = SparkConf().setAppName("question1").setMaster("local[*]")
sc = SparkContext(conf=conf)
# rdd = sc.parallelize(range(1, 4)).map(lambda x: (x, "a" * x))
# rdd.saveAsSequenceFile("motherfucker")
# print(sorted(sc.sequenceFile("motherfucker").collect()))
lines = sc.textFile(','.join(files_path))
lineLengths = lines.map(lambda s: len(s))
totalLength = lineLengths.reduce(lambda a, b: a + b)
