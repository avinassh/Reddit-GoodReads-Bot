#!/usr/bin/env python

import re
from xml.parsers.expat import ExpatError

import requests
import xmltodict

from settings import goodreads_api_key


def get_goodreads_ids(comment_msg):
    # receives goodreads url
    # returns the id using regex
    regex = r'goodreads.com/book/show/(\d+)'
    return set(re.findall(regex, comment_msg))


def get_book_details_by_id(goodreads_id):
    api_url = 'http://goodreads.com/book/show/{0}?format=xml&key={1}'
    r = requests.get(api_url.format(goodreads_id, goodreads_api_key))
    try:
        book_data = xmltodict.parse(r.content)['GoodreadsResponse']['book']
    except (TypeError, KeyError, ExpatError):
        return False
    keys = ['title', 'average_rating', 'ratings_count', 'description',
            'num_pages']
    book = {}
    for k in keys:
        book[k] = book_data[k]
    if type(book_data['authors']['author']) == list:
        authors = [author['name'] for author in book_data['authors']['author']]
        authors = ', '.join(authors)
    else:
        authors = book_data['authors']['author']['name']
    book['authors'] = authors
    return book
