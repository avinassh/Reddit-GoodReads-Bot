#!/usr/bin/env python

import time

import praw
from peewee import *
from peewee import OperationalError
from peewee import DoesNotExist

from goodreadsapi import get_book_details_by_id, get_goodreads_ids
from settings import reddit_username, reddit_password

# instantiate goodreads and reddit clients
user_agent = 'Goodreads, v0.1. Gives info of the book whenever goodreads\
link to a book is posted. (by /u/avinassh)'
reddit_client = praw.Reddit(user_agent=user_agent)
reddit_client.login(reddit_username, reddit_password)

replied_comments = []
last_checked_comment = None
db = SqliteDatabase('goodreadsbot.db')


class RepliedComments(Model):
    comment_id = CharField()
    author = CharField()
    subreddit = CharField()

    class Meta:
        database = db


def initialize_db():
    db.connect()
    try:
        db.create_tables([RepliedComments])
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


def log_this_comment(comment):
    comment_data = RepliedComments(comment_id=comment.id,
                                   author=comment.author.name,
                                   subreddit=comment.subreddit.title)
    comment_data.save()
    replied_comments.append(comment.id)


def reply_to_thanked_user(comment_id):
    # whenever a user says thanks reply to him!
    #
    # make sure the parent author is bot
    pass


def get_latest_comments(subreddit='india'):
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
                                           book['description'])
        message += '\n\n---\n\n'
    message += 'Bleep, Blop, Bleep! I am still in beta, please be ~~genital~~ ~~gental~~ fuck, be nice.'
    return message


def main():
    while True:
        global last_checked_comment
        for comment in get_latest_comments():
            if comment.id == last_checked_comment:
                time.sleep(30)
                break
            last_checked_comment = comment.id
            if 'goodreads.com' not in comment.body:
                continue
            if is_already_replied(comment.id):
                time.sleep(30)
                break
            goodread_ids = get_goodreads_ids(comment.body)
            if not goodread_ids:
                continue
            log_this_comment(comment)
            spool = [get_book_details_by_id(gr_id) for gr_id in goodread_ids]
            message = prepare_the_message(spool)
            comment.reply(message)
        # check if someone has replied to me


if __name__ == '__main__':
    initialize_db()
    main()
    deinit()
