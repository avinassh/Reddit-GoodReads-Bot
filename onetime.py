#!/usr/bin/env python

# this meant to be run once only, for a bot as recommended here -
# https://github.com/avinassh/prawoauth2
# taken from example here -
# https://github.com/avinassh/prawoauth2/blob/master/examples/halflife3-bot/onetime.py

import praw
from prawoauth2 import PrawOAuth2Server

from settings import user_agent, scopes, app_key, app_secret

reddit_client = praw.Reddit(user_agent=user_agent)
oauthserver = PrawOAuth2Server(reddit_client, app_key=app_key,
                               app_secret=app_secret, state=user_agent,
                               scopes=scopes)

# start the server, this will open default web browser
# asking you to authenticate
oauthserver.start()
print(oauthserver.get_access_codes())
