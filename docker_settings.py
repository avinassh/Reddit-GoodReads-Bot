# this file will be used by Docker where secrets are from ENV
# Check Dockerfile
# Rename this file to `settings.py` in deployment

import os

from common_settings import *

# reddit app
app_key = os.getenv("REDDIT_APP_KEY")
app_secret = os.getenv("REDDIT_APP_SECRET")

# bot account
username = os.getenv("BOT_USERNAME")
password = os.getenv("BOT_PASSWORD")

# good reads
goodreads_api_key = os.getenv("GOODREADS_API_KEY")
goodreads_api_secret = os.getenv("GOODREADS_API_SECRET")
