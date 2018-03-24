# -*- coding: utf-8 -*-
import json
import requests
from requests_oauthlib import OAuth1
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from datetime import datetime
import emoji

if not CONSUMER_KEY or not CONSUMER_SECRET or not ACCESS_TOKEN or not ACCESS_TOKEN_SECRET:
    raise ValueError('settings.pyでAPI_KEYを設定してください.')


class TweetEntry:
    def __init__(self, items):
        self.items = items

    def tweet_id(self):
        return str(self.items['id'])

    def user_id(self):
        return str(self.items['user']['id'])

    def created_at(self):
        return trans_timestamp(int(self.items['timestamp_ms'][:10]))

    def text(self):
        return rm_newline(rm_emoji(self.items['text']))

    def name(self):
        return rm_emoji(self.items['user']['name'])

    def source(self):
        return pickup_source(rm_emoji(self.items['source']))

    def description(self):
        return rm_newline(rm_emoji(self.items['user']['description']))

    def location(self):
        return rm_emoji(self.items['user']['location'])

    def screen_name(self):
        return self.items['user']['screen_name']

    def reply_count(self):
        return int(self.items['reply_count'])

    def favorite_count(self):
        return int(self.items['favorite_count'])

    def retweet_count(self):
        return int(self.items['retweet_count'])

    def friends_count(self):
        return int(self.items['user']['friends_count'])

    def followers_count(self):
        return int(self.items['user']['followers_count'])

    def statuses_count(self):
        return int(self.items['user']['statuses_count'])

    def media_type(self):
        if 'extended_entities' in self.items and 'media' in self.items['extended_entities']:
            media_type = self.items['extended_entities']['media'][0]['type']
            return media_type
        else:
            return None

    def country(self):
        place = self.items['place']
        return place['country'] if place else None

    def place(self):
        place = self.items['place']
        return place['full_name'] if place else None


def rm_newline(text):
    """改行をスペースに変換"""
    return text.replace('\n', ' ') if text else None


def trans_timestamp(timestamp):
    """UnixTime->Datetimeに変換"""
    return datetime.fromtimestamp(timestamp)


def rm_emoji(text):
    """絵文字を除去"""
    return ''.join(char for char in text if char not in emoji.UNICODE_EMOJI) if text else None


def pickup_source(s):
    """sourceのHTMLタグを除去"""
    return s.split('>')[1][:-3] if s else None


def show_tweet_entry(entry):
    print('tweet_id: ', entry.tweet_id())
    print('user_id: ', entry.user_id())
    print('created_at: ', entry.created_at())
    print('text: ', entry.text())
    print('location: ', entry.location())
    print('screen_name: ', entry.screen_name())
    print('reply_count: ', entry.reply_count())
    print('favorite_count: ', entry.favorite_count())
    print('retweet_count: ', entry.retweet_count())
    print('friends_count: ', entry.friends_count())
    print('followers_count: ', entry.followers_count())
    print('statuses_count: ', entry.statuses_count())
    print('media_type: ', entry.media_type())
    print('country: ', entry.country())
    print('place: ', entry.place())
    print()


def get_tweet_entries():
    for line in stream.iter_lines():
        try:
            items = json.loads(line.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            continue
        # リプライは除く
        if items['in_reply_to_status_id'] is not None:
            continue
        # RTは除く
        if 'retweeted_status' in items:
            continue
        yield TweetEntry(items)


if __name__ == '__main__':
    api = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    url = "https://stream.twitter.com/1.1/statuses/sample.json?language=ja"
    # data = {'follow': 'screen_name', 'track': 'keyword', 'location': 'location'}
    data = {}
    stream = requests.post(url, auth=api, stream=True, data=data)
    for entry in get_tweet_entries():
        show_tweet_entry(entry)
