#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger('GeocodingTweets')

import os, json, sys, re, csv, codecs
from scipy.spatial import cKDTree as KDTree
from math import sin, cos, sqrt, atan2, radians, isinf

def singleton(cls):
    """Singleton pattern to avoid loading class multiple times
    """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class TweetUSStateGeocoder:

    def __init__(self, geocode_filename='us_geocode.csv', us_places_to_state_mapping_filename='us.states.json'):
        coordinates, self.locations = self.extract_coordinates_and_locations(rel_path(geocode_filename))
        self.tree = KDTree(coordinates)

        self.us_places_to_state_map = self.load_us_places_to_state_mapping_file(rel_path(us_places_to_state_mapping_filename))

        # keep only alpha, space, period and comma
        self.keep_alpha_p = re.compile(r'[^a-zA-Z\s\.,]')

        self.geomap = {}

    def load_us_places_to_state_mapping_file(self, local_filename):
        if os.path.exists(local_filename):
            with open(local_filename, 'r') as rf:
                return json.load(rf)
        else:
            logger.error("missing us_places_to_state_mapping file: [%s]"%(local_filename))
            sys.exit(1)

    def extract_coordinates_and_locations(self, local_filename):
        """Extract geocode data from zip
        """
        if os.path.exists(local_filename):
            # open compact CSV
            rows = csv.reader(codecs.getreader('utf-8')(open(local_filename, 'rb')))
        else:
            logger.error("missing geocode file: [%s]"%(local_filename))
            sys.exit(1)

        # load a list of known coordinates and corresponding locations
        coordinates, locations = [], []
        for latitude, longitude, state, place in rows:
            coordinates.append((latitude, longitude))
            locations.append(dict(state=state, city=place, latitude=latitude, longitude=longitude))
        return coordinates, locations

    def query_coordinates(self, coordinates):
        """Find closest match to this list of coordinates
        """
        try:
            distances, indices = self.tree.query(coordinates, k=1) #, distance_upper_bound=0.1
        except ValueError as e:
            logger.erro('Unable to parse coordinates:', coordinates)
            raise e
        else:
            results = []
            for distance, index in zip(distances, indices):
                if not isinf(distance):
                    result = self.locations[index]
                    result['distance'] = distance

                    results.append(result)

            return results

    def distance(self, coordinate_1, coordinate_2):

        R = 6373.0

        lat1, lon1 = coordinate_1
        lat2, lon2 = coordinate_2

        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance * 0.621371

    def get_by_coordinate(self, coordinate):
        """Search for closest known location to this coordinate
        """
        tug = TweetUSStateGeocoder()
        results = tug.query_coordinates([coordinate])
        return results[0] if results else None

    def search_by_coordinates(self, coordinates):
        """Search for closest known locations to these coordinates
        """
        tug = TweetUSStateGeocoder()
        return tug.query_coordinates(coordinates)

    def get_state(self, address):

        address = address.strip()

        state = None

        if address not in self.geomap:

            p = re.findall(r'.*?([-+]?\d*\.\d+),([-+]?\d*\.\d+)', address)

            if (len(p) > 0):
                coordinate = p.pop()
                nearest = self.get_by_coordinate(coordinate)

                if nearest:
                    c2 = nearest['latitude'], nearest['longitude']
                    d = self.distance(coordinate, c2)
                    if (d < 20): # less than 100 miles
                        state = nearest['state']
                        self.geomap[address] = state

            else:

                address_ = address.replace(', ', ',')
                address_ = re.sub(self.keep_alpha_p, '', address_)
                address_ = address_.lower()

                for i in range(3):
                    #state = us_places_to_state_map[address] if address in us_places_to_state_map else None
                    if address_ in self.us_places_to_state_map['%s'%i]:
                        state = self.us_places_to_state_map['%s'%i][address_]
                        self.geomap[address] = state
                        break
                        # logger.info('[%s]->%s'%(address, state))
        else:
            state = self.geomap[address]

        return state


def rel_path(filename):
    """Return the path of this filename relative to the current script
    """
    return os.path.join(os.getcwd(), os.path.dirname(__file__), filename)

# def distance(coordinate_1, coordinate_2):
#     tug = TweetUSGeocoder()
#     return tug.distance(coordinate_1, coordinate_2)

if __name__=="__main__":

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    tug = TweetUSStateGeocoder()

    logger.info(tug.get_state('xxx: (-37.81, 144.96)'))
    logger.info(tug.get_state('Little Rock, AR'))

    # test some coordinate lookups
    #city1 = (-37.81, 144.96)
    # city1 = (34.7240049,-92.3379275)
    # city2 = (35.7240049,-92.3379275)
    # logger.info(tug.distance(city1, city2))
    # city1 = (54.143,-165.7854)
    # #city2 = (31.76, 35.21)
    # nearest = tug.get_by_coordinate(city1)
    # logger.info(nearest)
    # if (nearest):
    #     nearest_city = nearest['latitude'], nearest['longitude']

    #     logger.info(tug.distance(city1, nearest_city))
    # #print(search([city1, city2]))
