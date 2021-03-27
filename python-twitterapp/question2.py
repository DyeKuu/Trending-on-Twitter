from prelude import *

with open(STOP_WORDS_PATH, 'r', encoding='utf-8') as f:
    stop_words = [i.strip() for i in f.readlines()]
stop_words.extend(['rt', ':', '?', ',', '.', '!',
                   '-', '_', '/', '»', '«', "c’est", "c'est", "j’ai", "j'ai"])

date_time_begin_str = 'Sat Feb 1 20:00:00 +0000 2020'
date_time_end_str = 'Sun Feb 2 20:00:00 +0000 2020'
date_time_pattern = '%a %b %d %H:%M:%S %z %Y'
date_time_begin_obj = datetime.datetime.strptime(
    date_time_begin_str, date_time_pattern)
date_time_end_obj = datetime.datetime.strptime(
    date_time_end_str, date_time_pattern)

conf = SparkConf().setAppName("question2").setMaster("local[*]")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

date_time_begin_obj_broadcast = sc.broadcast(date_time_begin_obj)
date_time_end_obj_broadcast = sc.broadcast(date_time_end_obj)
date_time_pattern_broadcast = sc.broadcast(date_time_pattern)
stop_words_broadcast = sc.broadcast(stop_words)

lines = sc.textFile(','.join(FILES_PATH))
lines = lines.map(lambda line: json.loads(line))


def filter_time_range(s):
    curr_datetime = datetime.datetime.strptime(
        s['created_at'], date_time_pattern_broadcast.value)
    return curr_datetime > date_time_begin_obj_broadcast.value and curr_datetime < date_time_end_obj_broadcast.value


words = lines.filter(filter_time_range)\
    .map(lambda d: d['text'].lower())\
    .flatMap(lambda s: s.strip().split())

most_frequent_word = words.filter(
    lambda w: w not in stop_words_broadcast.value)\
    .map(lambda x: (x, 1))\
    .reduceByKey(lambda a, b: a + b)\
    .max(key=lambda x: x[1])

print("Most Frequent word from {} to {} is: {} with occurence {}".format(
    date_time_begin_str, date_time_end_str, most_frequent_word[0], most_frequent_word[1]))
