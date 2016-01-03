#!/usr/bin/env python

import time
import json
import random

import praw
from peewee import *
from peewee import OperationalError
from peewee import DoesNotExist
import pypandoc
from prawoauth2 import PrawOAuth2Mini

from goodreadsapi import get_book_details_by_id, get_goodreads_ids
from settings import (app_key, app_secret, access_token, refresh_token,
                      user_agent, scopes, supported_subreddits,
                      be_gentle_to_reddit)

# instantiate goodreads and reddit clients

reddit_client = praw.Reddit(user_agent=user_agent)
oauth_helper = PrawOAuth2Mini(reddit_client, app_key=app_key,
                              app_secret=app_secret,
                              access_token=access_token,
                              refresh_token=refresh_token, scopes=scopes)

replied_comments = []
last_checked_comment = []
thanked_comments = []
db = SqliteDatabase('goodreadsbot.db')


with open('welcome_messages.json') as f:
    welcome_messages = json.load(f)['messages']


class RepliedComments(Model):
    comment_id = CharField()
    author = CharField()
    subreddit = CharField()

    class Meta:
        database = db


class ThankedComments(Model):
    comment_id = CharField()
    author = CharField()
    subreddit = CharField()

    class Meta:
        database = db


def initialize_db():
    db.connect()
    try:
        db.create_tables([RepliedComments, ThankedComments])
    except OperationalError:
        # Table already exists. Do nothing
        pass


def deinit():
    db.close()


def is_already_replied(comment_id):
    if comment_id in replied_comments:
        return True
    try:
        RepliedComments.select().where(
            RepliedComments.comment_id == comment_id).get()
        return True
    except DoesNotExist:
        return False


def is_already_thanked(comment_id):
    if comment_id in thanked_comments:
        return True


def log_this_comment(comment, TableName=RepliedComments):
    comment_data = TableName(comment_id=comment.id,
                             author=comment.author.name,
                             subreddit=comment.subreddit.display_name)
    comment_data.save()
    replied_comments.append(comment.id)


def get_a_random_message():
    return random.choice(welcome_messages)


def get_latest_comments(subreddit):
    subreddit = reddit_client.get_subreddit(subreddit)
    return subreddit.get_comments()


def prepare_the_message(spool):
    message_template = u"**Name**: {0}\n\n**Author**: {1}\n\n**Avg Rating**: {2} by {3} users\n\n**Description**: {4}\n\n Pages: {5}, Year: {6}"
    message = ""
    for book in spool:
        message += message_template.format(book['title'],
                                           book['authors'],
                                           book['average_rating'],
                                           book['ratings_count'],
                                           html_to_md(book['description']),
                                           book['num_pages'],
                                           book['publication_year'])
        message += '\n\n---\n\n'
    message += 'Bleep, Blop, Bleep! I am still in beta, please be be nice. Contact [my creator](https://www.reddit.com/message/compose/?to=avinassh) for feedback, bug reports or just to say thanks!'
    return message


def html_to_md(string):
    # remove the <br> tags before conversion
    if not string:
        return
    string = string.replace('<br>', ' ')
    return pypandoc.convert(string, 'md', format='html')


def take_a_nap():
    if be_gentle_to_reddit:
        time.sleep(30)


def goodreads_bot_serve_people(subreddit='india'):
    global last_checked_comment
    for comment in get_latest_comments(subreddit):
        if comment.id in last_checked_comment:
            break
        last_checked_comment.append(comment.id)
        if 'goodreads.com' not in comment.body:
            continue
        if is_already_replied(comment.id):
            break
        goodread_ids = get_goodreads_ids(comment.body)
        if not goodread_ids:
            continue
        spool = map(get_book_details_by_id, goodread_ids)
        message = prepare_the_message(spool)
        comment.reply(message)
        log_this_comment(comment)


def reply_to_self_comments():
    for comment in reddit_client.get_comment_replies():
        if is_already_thanked(comment_id=comment.id) or not comment.new:
            break
        comment.mark_as_read()
        if 'thank' in comment.body.lower():
            comment.reply(get_a_random_message())
            thanked_comments.append(comment.id)
            log_this_comment(comment, TableName=ThankedComments)


def main():
    while True:
        try:
            goodreads_bot_serve_people(subreddit=supported_subreddits)
            reply_to_self_comments()
        except praw.errors.OAuthInvalidToken:
            oauth_helper.refresh()

        take_a_nap()
        # break

if __name__ == '__main__':
    initialize_db()
    main()
    deinit()
