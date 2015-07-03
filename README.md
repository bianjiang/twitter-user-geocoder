
Twitter User Geocoder
==========

A utility to help you map Twitter users to specific states (or cities, this is more problematic, and the solution here isn't that reliable).

The name `geocoder` is a little misleading, as I wasn't attempt to resolve the location string to a set of geocodes (i.e., latitude and longitude).

The following information is somewhat from my paper (based on other papers that I have read, and my own experience). In some of our projects, we are trying to study regional differences (e.g., sentiments, public perceptions,etc.) based on Twitter data. For example, we studied how people use [(trans-)gender identification terminology](http://bianjiang.github.io/twitter-language-on-transgender/) differently across different regions; and test to see whether the gender identification terms used by the lgbt community is different from the general public (it's obviously true, but we need data to support this conclusion).

But anyway, back to the topic of geocoding. For geotagging, we extracted the ‘location’ field, part of a user’s profile, and attempted to assign a U.S. state to each tweet accordingly. Specifically, we searched each location field for a number of lexical patterns indicating the location of the user such as the name of a state (e.g., Arkansas or Florida), or a city name in combination with a state name or state abbreviation in various possible formats (e.g., “——, fl” or “——, florida” or “——, fl, usa”). Selfreported locations are often nonsensical (e.g., “wonder land” or “up in the sky”), but strict patterns produced good matches and helped to reduce the number of false positives.

Notably Twitter also provides the ability to attach geocodes (i.e., latitude and longitude) to a user’s profile and to each tweet. Yet, since geolocation needs to be enabled explicitly by the user as well as requires the user to have a device that is capable of capturing geocodes (e.g., a mobile phone with GPS turned on), very few tweets we have collected have this information. This is consistent with findings from previous studies. If the ‘location’ field was missing in a user’s profile, but the ‘geo’ attribute was available (or the geocodes are embedded in the `location` field, which is very common for third-party mobile apps that post Tweets on user's behalf early on), we attempted to resolve the location of the user through reverse geocoding via the publicly available GeoNames geographical database. However, we did not use the geocodes attached to each individual tweet since it is possible that a user was traveling away from their home state, in which case the geocodes attached to the tweets would be different from those on their profile. For our study, we geotagged the tweets based on where the user is from, not where the user is traveling temporarily. However, we do consider the scenario where a user permanently moved from one state to another reflected as a change in the ‘location’ field of a user’s profile.

Installation
------------

None... just clone this and start using it. It's not that complicated yet to have a setup.py..

    git clone git://github.com/bianjiang/twitter-user-geocoder.git

Dependencies
------------
I think this is Python 3 only. At least I haven't tested this on Python 2 yet. 

How to use
------------
It's basically trying to resolve the `location` string to a U.S. state or city based on lexical patterns. So, the first thing this tool does is to construct a dictionary based on [GeoNames](http://www.geonames.org/) database, which is done by running:

  $ ./bootstraph_geonames.sh

It downloads the relevant databases from geonames, and run `process_geonames_us.py` to generate the lexical dictionaries.

**Note that, the `bootstraph_geonames.sh` uses `aria2c` to download the file, and I uses [pyenv](https://github.com/yyuu/pyenv) to manage my python versions.**

**I included the dictionaries I have generated in this repo. The `us.states.json` is too big, so I have to compressed it (with `gzip`). Before you use it, you have to unzip it first.**

**You should regenerate the dictionaries, since GeoNames databases are still growing. But there are a few caveats (see below), so I had to manually fix a few lexical patterns. **

Now, I split the code into two `tweet_us_city_geocoder.py` and `tweet_us_state_geocoder.py`. And the functionality of each is obvious based on the names. At the end of each script you see a test case.

For `tweet_us_state_geocoder.py`, the output is the two-letter abbreviated state names or `None` if the geocodes out side of US.

  ```python

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    tug = TweetUSStateGeocoder()

    logger.info(tug.get_state('xxx: (-37.81, 144.96)')) # output None, geocodes out side of US
    logger.info(tug.get_state('Little Rock, AR')) # output 'ar'

  ```

For `tweet_us_city_geocoder.py`, the output is a `dict` object.

  ```python
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    tug = TweetUSCityGeocoder()

    logger.info(tug.get_city_state('xxx: (39.76838,-86.15804)')) # output ({'city': 'indianapolis', 'state': 'in'})
  ```

The output is:

  ```python
    {'city': 'indianapolis', 'state': 'in'}
  ```


Caveats
------------
There are a number of issues such as the data in GeoNames isn't complete. But the biggest issue is duplicated city names. So I had to make a choice between e.g., hollywood, ca vs. hollywood, fl, when you see a `location` string of `hollywood`. This is obvious, you will choose `hollywood, ca`, but you have to realize that you will have no tweets being categorized as from `hollywood, fl` any more. It's a trade-off that you have to make. 

For the dictionaries I included in this repo, I manually fixed a lot of this based on my own use-case.

#### Cities with duplicate names:

# INFO: ['hollywood', 'kansas city', 'peoria', 'columbia', 'springfield', 'columbus', 'glendale', 'aurora']

hollywood, ca vs. hollywood, fl
  ````
  {
    "names": ["hollywood"],
    "state": "fl",
    "city": "hollywood"
  }
  ````

kansas city, mo vs. kansas city, ks (They are the same, border city)

peoria, il vs. north peoria, il vs. peoria, az (Treat it as peoria, il)
{
  "names": ["peoria"],
  "state": "az",
  "city": "peoria"
}

los angeles, vs. east los angeles (Take los angeles)

las vegas vs. north las vegas (Take las vegas)
{
  "names": ["north las vegas"],
  "state": "nv",
  "city": "north las vegas"
}

columbia, sc vs. columbia, mo (Take columbia, sc, but removed since it's confusing with district of columbia)
{
  "names": ["columbia"],
  "state": "mo",
  "city": "columbia"
}

springfield, mo vs. springfield, ma vs. springfield, il (Take springfield, mo)

chattanooga, tn vs. east chattanooga, tn (Take chattanooga, tn)

columbus, oh vs. columbus, ga (Take columnbus, oh)

glendale, ca vs north glendale, ca vs. glendale, az (Take glendale, ca)

aurora, co vs. aurora, il (Take aurora, co)

independence, mo vs. east independence, mo (Take independence, mo)

boston, ma vs. south boston, ma (Take boston, ma)

memphis, tn vs. new south memphis, tn (Take memphis, tn)

raleigh, nc vs. west raleigh, nc (Take raleigh, nc)

### License
------------

The MIT License (MIT)
Copyright (c) 2015 Jiang Bian (ji0ng.bi0n@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
