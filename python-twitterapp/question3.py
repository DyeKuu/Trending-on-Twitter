from prelude import *

with open(STOP_WORDS_PATH, 'r', encoding='utf-8') as f:
    stop_words = [i.strip() for i in f.readlines()]
stop_words.extend(['rt', ':', '?', ',', '.', '!',
                   '-', '_', '/', '»', '«', "c’est", "c'est", "j’ai", "j'ai"])

date_time_pattern = '%a %b %d %H:%M:%S %z %Y'
local_timezone = pytz.timezone("Europe/Paris")

conf = SparkConf().setAppName("question3").setMaster("local[*]")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

local_timezone_broadcast = sc.broadcast(local_timezone)
date_time_pattern_broadcast = sc.broadcast(date_time_pattern)
stop_words_broadcast = sc.broadcast(stop_words)
NIGHT_BEGIN_BROADCAST = sc.broadcast(NIGHT_BEGIN)
NIGHT_END_BROADCAST = sc.broadcast(NIGHT_END)

lines = sc.textFile(','.join(FILES_PATH))
lines = lines.map(lambda line: json.loads(line))


def isNight(s):
    curr_hour = datetime.datetime.strptime(
        s['created_at'], date_time_pattern_broadcast.value).astimezone(local_timezone_broadcast.value).hour
    return curr_hour >= NIGHT_BEGIN_BROADCAST.value or curr_hour <= NIGHT_END_BROADCAST.value


night_words = lines.filter(isNight)\
    .map(lambda d: d['text'].lower())\
    .flatMap(lambda s: s.strip().split())

night_words_count = night_words.filter(
    lambda w: w not in stop_words_broadcast.value)\
    .map(lambda x: (x, 1))\
    .reduceByKey(lambda a, b: a + b)

day_words = lines.filter(lambda x: not isNight(x))\
    .map(lambda d: d['text'].lower())\
    .flatMap(lambda s: s.strip().split())

day_words_count = day_words.filter(
    lambda w: w not in stop_words_broadcast.value)\
    .map(lambda x: (x, 1))\
    .reduceByKey(lambda a, b: a + b)


def calDiffAndReverse(x):
    if x[1][1] is None:
        return (x[1][0], x[0])
    return (x[1][0] - x[1][1], x[0])


result = night_words_count.leftOuterJoin(day_words_count).map(
    calDiffAndReverse).sortByKey(False).take(10)

print("Top 10 most frequent words only in evening:")
print(result)
