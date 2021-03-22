from pyspark.sql import SparkSession, SQLContext
from pyspark import SparkContext, SparkConf
import json
import datetime
import os
import pytz

DATA_PATH = '../data/French/'
FILES = os.listdir(DATA_PATH)
FILES_PATH = [DATA_PATH+f for f in FILES]
STOP_WORDS_PATH = 'helper_data/stop_words_french.txt'
NIGHT_BEGIN = 18
NIGHT_END = 6
