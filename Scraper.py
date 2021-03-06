import time
from datetime import datetime

import praw
import pymongo
from pymongo import MongoClient

import yfinance as yf

def main():
    client = MongoClient('localhost', 27017)
    collection = client["fnGME"]["top_10"]

    nasdaq_dict = {}
    nyse_dict = {}
    ticker_dict = {}

    with open("Ticker Symbols/NASDAQ.txt", "r") as nasdaq:
        lines = [line.strip() for line in nasdaq.readlines()]
        for line in lines:
            if len(line.split("\t")) >= 2:
                symbol = line.split("\t")[0]
                name = line.split("\t")[1]
                nasdaq_dict[symbol] = name
                ticker_dict[symbol] = name
            # else:
            #     print(f"empty line in nasdaq: {line}")

        # print(nasdaq_dict)

    with open("Ticker Symbols/NYSE.txt", "r") as nyse:
        lines = [line.strip() for line in nyse.readlines()]
        for line in lines:
            if len(line.split("\t")) >= 2:
                symbol = line.split("\t")[0]
                name = line.split("\t")[1]
                nyse_dict[symbol] = name
                if symbol not in ticker_dict:
                    #     print(f"{symbol} already exists in NASDAQ")
                    # else:
                    ticker_dict[symbol] = name
            # else:
            #     print(f"empty line in nyse: {line}")

    reddit = praw.Reddit(client_id="3j4aMHa4CXXC7Q", client_secret="84T5rXSssKEm5H07XBIJ4wgo1MDdRw",
                         user_agent="for testing")

    hot_posts = reddit.subreddit("wallstreetbets").hot(limit=None)

    # print(type(hot_posts))

    def add_to_dict(word_in_post, ticker_dict):
        for word in word_in_post:
            clean_word = word.strip()
            if clean_word in ticker_dict:
                ticker_count.setdefault(clean_word, 0)
                ticker_count[clean_word] += 1
            # else:
            #     print(f"{clean_word} not in ticker list")

    ticker_count = {}
    # counter = 0
    for post in hot_posts:
        # print(f"This is the {counter} post content - "
        #       f"title: {post.title}"
        #       f"content: {post.selftext}")
        # counter +=1
        word_in_title = post.title.split()
        add_to_dict(word_in_title, ticker_dict)
        word_in_content = post.selftext.split()
        add_to_dict(word_in_content, ticker_dict)

    # print(ticker_count)

    sorted_ticker_count = dict(sorted(ticker_count.items(), key=lambda item: item[1], reverse=True))

    # print(sorted_ticker_count)
    # print(f"Before clean {len(ticker_count)}")

    # A list of abbreviations generally do not represent tickers.
    black_list = ["A", "DD", "FOR", "CEO", "ALL", "EV", "OR", "AT", "RH", "ONE", "ARE", "VERY", "ON"]

    clean_sorted_ticker_dict = {}

    for key, value in sorted_ticker_count.items():
        if key not in black_list:
            clean_sorted_ticker_dict[key] = value

    # print(clean_sorted_ticker_dict)
    # print(f"After clean {len(clean_sorted_ticker_dict)}")

    sorted_ticker_list = list(clean_sorted_ticker_dict.keys())

    # top10_toDB = {}
    now = datetime.now()
    for i in range(10):
        output_ticker = sorted_ticker_list[i]
        output_count = clean_sorted_ticker_dict[output_ticker]
        toDB = {
            "rank": i+1,
            "ticker": output_ticker,
            "name": ticker_dict[output_ticker],
            "count": output_count,
            "timeStamp": now
        }
        print(toDB)
        collection.insert_one(toDB)
        # top10_toDB[str(i)] = (output_ticker, output_count)
        # print(f"{output_ticker}: {output_count}")

    # collection.insert_one(top10_toDB)

    # print(top10_toDB)




if __name__ == "__main__":
    # while True:
    main()
    # time_wait = 10
    # time.sleep(time_wait * 60)
    # print(f"Waiting {time_wait} minutes, now is {datetime.now()}")
