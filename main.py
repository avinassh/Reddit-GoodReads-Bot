#!/usr/bin/env python

import praw
from goodreads import client

from goodreadsapi import get_book_details_by_id, get_goodreads_ids
from settings import (goodreads_api_key,
                      goodreads_api_secret,
                      reddit_username,
                      reddit_password)

# instantiate goodreads and reddit clients
user_agent = 'Goodreads, v0.1. Gives info of the book whenever goodreads\
link to a book is posted. (by /u/avinassh)'
reddit_client = praw.Reddit(user_agent=user_agent)
reddit_client.login(reddit_username, reddit_password)
gr_client = client.GoodreadsClient(goodreads_api_key, goodreads_api_secret)


def reply_to_thanked_user(comment_id):
    # whenever a user says thanks reply to him!
    #
    # make sure the parent author is bot
    pass


def get_latest_comments(subreddit='india'):
    subreddit = reddit_client.get_subreddit(subreddit)
    return subreddit.get_comments()


def prepare_the_message(spool):
    message_template = u"**Name**: {0}\n\n**Author**: {1}\n\n\
    **Avg Rating**: {2} by {3} users\n\n**Description**: {4}"
    message = ""
    for book in spool:
        message += message_template.format(book['title'],
                                           book['authors'],
                                           book['average_rating'],
                                           book['ratings_count'],
                                           book['description'])
        message += '\n\n---\n\n'
    message += 'Bleep, Blop, Bleep!'
    return message


def main():
    while True:
        for comment in get_latest_comments('TESTBOTTEST'):
            if 'goodreads.com' not in comment.body:
                continue
            goodread_ids = get_goodreads_ids(comment.body)
            if not goodread_ids:
                continue
            # log comment.id
            spool = [get_book_details_by_id(gr_id) for gr_id in goodread_ids]
            message = prepare_the_message(spool)
            comment.reply(message)
            break
        break
        # check if someone has replied to me


if __name__ == '__main__':
    main()
