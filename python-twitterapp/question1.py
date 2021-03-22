from pyspark.sql import SparkSession, SQLContext
from pyspark import SparkContext, SparkConf
import json
import datetime
from config import FILES_PATH
date_time_begin_str = 'Sat Feb 1 20:00:00 +0000 2020'
date_time_end_str = 'Sun Feb 2 20:00:00 +0000 2020'
date_time_pattern = '%a %b %d %H:%M:%S %z %Y'
date_time_begin_obj = datetime.datetime.strptime(
    date_time_begin_str, date_time_pattern)
date_time_end_obj = datetime.datetime.strptime(
    date_time_end_str, date_time_pattern)

conf = SparkConf().setAppName("question1").setMaster("local[*]")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)
lines = sc.textFile(','.join(FILES_PATH))
lines = lines.map(lambda line: json.loads(line))


def filter_time_range(s):
    curr_datetime = datetime.datetime.strptime(
        s['created_at'], date_time_pattern)
    return curr_datetime > date_time_begin_obj and curr_datetime < date_time_end_obj


words = lines.filter(filter_time_range)\
    .map(lambda d: d['text'])\
    .flatMap(lambda s: s.strip().split())

most_frequent_word = words.map(lambda x: (x, 1))\
    .reduceByKey(lambda a, b: a + b)\
    .max(key=lambda x: x[1])

print("Most Frequent word from {} to {} is: {} with occurence {}".format(
    date_time_begin_str, date_time_end_str, most_frequent_word[0], most_frequent_word[1]))
