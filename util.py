#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger('GeocodingTweets')

bad_locations = ['spain', 'nowhere']

def bad_location(location):

    location = location.lower()

    for bad_location in bad_locations:
        if (bad_location in location):
            return True

    return False