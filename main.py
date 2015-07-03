#!/usr/bin/env python

import time
import json
import random

import praw
from peewee import *
from peewee import OperationalError
from peewee import DoesNotExist
import pypandoc

from goodreadsapi import get_book_details_by_id, get_goodreads_ids
from settings import reddit_username, reddit_password

# instantiate goodreads and reddit clients
user_agent = 'Goodreads, v0.1. Gives info of the book whenever goodreads\
link to a book is posted. (by /u/avinassh)'
reddit_client = praw.Reddit(user_agent=user_agent)
reddit_client.login(reddit_username, reddit_password)

replied_comments = []
last_checked_comment = []
be_gentle_to_reddit = True
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


def log_this_comment(comment, TableName=RepliedComments):
    comment_data = TableName(comment_id=comment.id,
                             author=comment.author.name,
                             subreddit=comment.subreddit.title)
    comment_data.save()
    replied_comments.append(comment.id)


def get_a_random_message():
    return random.choice(welcome_messages)


def get_latest_comments(subreddit):
    subreddit = reddit_client.get_subreddit(subreddit)
    return subreddit.get_comments()


def prepare_the_message(spool):
    message_template = u"**Name**: {0}\n\n**Author**: {1}\n\n**Avg Rating**: {2} by {3} users\n\n**Description**: {4}"
    message = ""
    for book in spool:
        message += message_template.format(book['title'],
                                           book['authors'],
                                           book['average_rating'],
                                           book['ratings_count'],
                                           html_to_md(book['description']))
        message += '\n\n---\n\n'
    message += 'Bleep, Blop, Bleep! I am still in beta, please be ~~genital~~ ~~gental~~ fuck, be nice.'
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
        if not comment.new:
            break
        comment.mark_as_read()
        if 'thank' in comment.body.lower():
            comment.reply(get_a_random_message())
            log_this_comment(comment, TableName=ThankedComments)


def main():
    while True:
        goodreads_bot_serve_people(subreddit='testtesttest')
        reply_to_self_comments()
        take_a_nap()
        break

if __name__ == '__main__':
    initialize_db()
    main()
    deinit()
