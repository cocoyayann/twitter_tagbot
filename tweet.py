import tweepy
from json import load
import csv
import time
from datetime import datetime

now_time = datetime.now().strftime('%Y-%m-%dT%H:%M:00+09:00')

config_file = "/home/user/config.json"
block_file = "/home/user/block.csv"

with open(config_file) as f:
    config_dict = load(f)

with open(block_file, mode="r") as f:
    block_list = list(csv.reader(f))
    block_list = [i[0] for i in block_list[1:]]


api_key = "*********"
api_key_secret = "***********"


def search(query, since_id):
    expansions = ["author_id"]
    tweet_fields = ["entities"]

    res = client.search_recent_tweets(
        query,
        max_results=100,
        expansions=expansions,
        tweet_fields=tweet_fields,
        since_id=since_id,
        user_auth=True
    )

    count = res.meta["result_count"]

    if count==0:
        return count, None
    else:
        data = list(reversed(res.data))
        return count, data

def id_filter(data):
    user_id = str(data["author_id"])
    tag_num = len(data['entities']['hashtags'])

    if user_id in block_list:
        return False, "block"
    elif tag_num > 6:
        return False, "excessive_tags"
    else:
        return True, "retweet"

for config in config_dict.items():

    query = config[1]["query"]
    log_file = config[1]["log_file"]
    access_token = config[1]["access_token"]
    access_token_secret = config[1]["access_token_secret"]

    with open(log_file) as f:
        log_list = list(csv.reader(f))
        since_id = log_list[-1][3]

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    count, data_list = search(query, since_id)

    if count==0:
        continue
        
    for data in data_list:
        TF, status = id_filter(data)

        if TF==True:client.retweet(data["id"])

        log_list = [now_time, status, data["author_id"], data["id"]]

        with open(log_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(log_list)
