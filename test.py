#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import logging.handlers

logger = logging.getLogger('ProcessGeoname')
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

import csv, codecs, sys, json, os, copy
import collections

def check_duplicates():
    us_cities_file = os.path.abspath('./geocoding/us.cities.json')
    cities = []
    with open(us_cities_file, 'r') as rf:
        for city in json.load(rf):
            cities.append(city['city'])

        logger.info([x for x, y in collections.Counter(cities).items() if y > 1])

        logger.info(len(set(cities)))

        # INFO: ['hollywood', 'kansas city', 'peoria', 'columbia', 'springfield', 'columbus', 'glendale', 'aurora']

if __name__ == "__main__":

    logger.info(sys.version)

    check_duplicates()
