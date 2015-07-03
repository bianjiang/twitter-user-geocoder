#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import logging.handlers

logger = logging.getLogger('ProcessGeoname')
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)


import csv, codecs, sys, json, os, util

csv.field_size_limit(sys.maxsize)

def prepare_us_places_to_state_mapping():

    def build_non_us_places():
        non_us_places = []
        with codecs.getreader('utf-8')(open('allCountries.txt', 'rb')) as f:
            reader = csv.reader(f, delimiter='\t')
            cnt = 0
            for row in reader:
                country = row[8].lower().strip()
                state = row[10].lower().strip()
                name = row[1].lower().strip()

                if country != 'us':
                    non_us_places.append(name)

        return non_us_places

    non_us_places = build_non_us_places()
    non_us_places.extend(util.bad_locations) # noticed bad location names

    non_us_places = set(non_us_places)

    features = {
        0: {}, #state
        1: {}, #city
        2 : {} #county
    }

    state_lookup = {}

    country_alternate_names = ['us', 'u.s.', 'u.s', 'u.s.a.', 'u.s.a', 'usa', 'united states']#, 'united states of america', 'america']
    country = 'us'
    #build state lookup
    with codecs.getreader('utf-8')(open('zip_US.txt', 'rb')) as f:
        reader = csv.reader(f, delimiter='\t')

        for row in reader:
            state_name = row[3].lower().strip()

            if (not state_name):
                continue
            state = row[4].lower().strip()

            place = row[2].lower().strip()

            features[0][state] = state
            features[0][state_name] = state
            for country in country_alternate_names:
                features[0]['%s,%s'%(state, country)] = state
                features[0]['%s %s'%(state, country)] = state
                features[0]['%s,%s'%(state_name, country)] = state
                features[0]['%s %s'%(state_name, country)] = state

            state_lookup[state] = state_name

            if (place not in non_us_places):
                features[1][place] = state
            features[1]['%s,%s'%(place, state)] = state
            features[1]['%s,%s'%(place, state_name)] = state
            for country in country_alternate_names:
                features[1]['%s,%s'%(place, country)] = state
                features[1]['%s,%s,%s'%(place, state, country)] = state
                features[1]['%s,%s,%s'%(place, state_name, country)] = state

            features[1]['%s %s'%(place, state)] = state
            features[1]['%s %s'%(place, state_name)] = state
            for country in country_alternate_names:
                features[1]['%s %s'%(place, country)] = state
                features[1]['%s %s %s'%(place, state, country)] = state
                features[1]['%s %s %s'%(place, state_name, country)] = state

    with codecs.getreader('utf-8')(open('US.txt', 'rb')) as f:
        reader = csv.reader(f, delimiter='\t')
        cnt = 0
        for row in reader:

            country = row[8].lower().strip()
            state = row[10].lower().strip()
            name = row[1].lower().strip()

            if country != 'us':
                continue

            #feature class see http://www.geonames.org/export/codes.html, char(1)
            if (row[6].strip() not in ('A', 'P')):
                continue

            featureClassCode = row[7].strip()

            # admin1 - admin4
            #logger.info('%s, %s, %s, %s'%(row[10], row[11], row[12], row[13]))
            #ADM1 -> state
            #ADM2 -> County
            #ADM3 -> Village
            #ADM4 -> Doesn't exist

            # state already processed
            # if(featureClassCode == 'ADM1'):
            #     features[0][name] = state
            #     for c in country_alternate_names:
            #         features[0]['%s,%s'%(name, c)] = state
            #         features[0]['%s %s'%(name, c)] = state
            #     features[0][state] = state
            #     cnt += 1

            # if(name == 'kentucky'):
            #     logger.info(row)
            # # county
            if(featureClassCode == 'ADM2'):
                if (name not in non_us_places):
                    features[2][name] = state
                features[2]['%s,%s'%(name, state)] = state
                features[2]['%s,%s'%(name, state_lookup[state])] = state
                for country in country_alternate_names:
                    features[2]['%s,%s'%(name, country)] = state
                    features[2]['%s,%s,%s'%(name, state, country)] = state
                    features[2]['%s,%s,%s'%(name, state_lookup[state], country)] = state

                features[2]['%s %s'%(name, state)] = state
                features[2]['%s %s'%(name, state_lookup[state])] = state
                for country in country_alternate_names:
                    features[2]['%s %s'%(name, country)] = state
                    features[2]['%s %s %s'%(name, state, country)] = state
                    features[2]['%s %s %s'%(name, state_lookup[state], country)] = state

                cnt += 1
            elif(featureClassCode == 'PPL'):
                if (name not in non_us_places):
                    features[1][name] = state
                features[1]['%s,%s'%(name, state)] = state
                features[1]['%s,%s'%(name, state_lookup[state])] = state
                for country in country_alternate_names:
                    features[1]['%s,%s'%(name, country)] = state
                    features[1]['%s,%s,%s'%(name, state, country)] = state
                    features[1]['%s,%s,%s'%(name, state_lookup[state], country)] = state

                features[1]['%s %s'%(name, state)] = state
                features[1]['%s %s'%(name, state_lookup[state])] = state
                for country in country_alternate_names:
                    features[1]['%s %s'%(name, country)] = state
                    features[1]['%s %s %s'%(name, state, country)] = state
                    features[1]['%s %s %s'%(name, state_lookup[state], country)] = state

                cnt += 1


            if (cnt % 10000 == 0):
                logger.info('%d'%(cnt))

        logger.info(cnt)

        feature_file = os.path.abspath('us.states.json')

        with open(feature_file, 'w') as wf:
            json.dump(features, wf)

def prepare_reverse_gecoding_data_by_zip_us():

    with codecs.getreader('utf-8')(open('zip_US.txt', 'rb')) as f, open('us_geocode.csv', 'w') as of:
        reader = csv.reader(f, delimiter='\t')
        writer = csv.writer(of)
        for row in reader:
            state_name = row[3].lower().strip()

            if (not state_name):
                continue
            state = row[4].lower().strip()

            place = row[2].lower().strip()

            latitude, longitude = row[9:11]

            line = latitude, longitude, state, place
            writer.writerow(line)

def read_us_cities():
    cities = []
    with codecs.getreader('utf-8')(open('cities1000.txt', 'rb')) as rf:
        reader = csv.reader(rf, delimiter='\t')
        for row in reader:

            country = row[8].lower().strip()

            if (country != 'us'):
                continue

            state = row[10].lower().strip()

            population = int(row[14].lower().strip())

            name = row[1].lower().strip()

            alternate_names = row[3].lower().strip()

            latitude, longitude = row[4:6]

            #logger.info(row)
            #logger.info("[%s], [%s], [%s]: [%d], (%s, %s)"%(name, state, country, population, latitude, longitude))

            cities.append({
                "name": name,
                "alternate_names": alternate_names,
                "latitude": latitude,
                "longitude": longitude,
                "state": state,
                "country": country,
                "population": population
            })

    return cities

def prepare_us_city_mapping():
    cities = read_us_cities()

    cities = sorted(cities, key=lambda k: k['population'], reverse=True)

    output = []
    for city in cities:

        population = int(city['population'])
        if (population < 100000):
            continue

        names = [city['name']]
        #alternate_names = city['alternate_names'].split(',')

        # for alternate_name in alternate_names:
        #
        #     alternate_name = alternate_name.strip()
        #
        #     try:
        #         lang = detect(alternate_name)
        #
        #         if (lang == 'en'):
        #             names.append(alternate_name)
        #     except:
        #         pass

        output.append({
            'city': city['name'],
            'state': city['state'],
            'names': names
        })

    logger.info("total cities (population > 100k): %d"%(len(output)))
    us_cities_file = os.path.abspath('us.cities.json')

    with open(us_cities_file, 'w') as wf:
        json.dump(output, wf)


def prepare_reverse_gecoding_data_by_cities_us():

    cities = read_us_cities()

    cities = sorted(cities, key=lambda k: k['population'], reverse=True)

    with open('us_cities_geocode.csv', 'w') as of:
        writer = csv.writer(of)

        for city in cities:
            population = int(city['population'])
            if (population < 100000):
                continue

            line = city['latitude'], city['longitude'], city['state'], city['name']
            writer.writerow(line)


if __name__ == "__main__":
    logger.info(sys.version)

    # prepare_reverse_gecoding_data_by_cities_us()
    # prepare_us_city_mapping()

    prepare_reverse_gecoding_data_by_zip_us()
    prepare_us_places_to_state_mapping()
