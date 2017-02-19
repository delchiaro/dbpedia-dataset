import json
import time
from enum import Enum

from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from gpsAddressQuery import gpsToAddress

from artwork.artwork import Artwork, Museum

# Input
from utils.listRefactor import *
from utils import todict

DEFAULT_INPUT_FILE = "json/big_db.json"
OUTPUT_FILE = "json/big_db_organized_gpsConversion.json"

GPS_SERVER_REQUEST_DELAY = 4  # seconds delay for each request
GPS_SERVER_REQUEST_DELAY_IF_ERROR_429 = 1800

# Flags:
request_user_action_if_errror_429 = False
print_gps_address_info = True
print_location = False
print_artwork = False

gps_to_address = True  # convert GPS informations (if available) to address

# Query Keys:
QK_ARTWORK = "artwork"
QK_TITLE = "dbp_title"
QK_LABEL = "rdfs_label"  # todo new
QK_NAME = "foaf_name"  # todo new
QK_THUMB = "dbo_thumbnail"  # todo new
QK_IMG = "foaf_depiction"  # todo new

QK_DESCRIPTION = "dbo_abstract"
QK_COMMENT = "rdfs_comment"

QK_LAT = "geo_lat"
QK_LNG = "geo_long"
QK_LATLNG = "georss_point"
QK_LOCATION = "dbo_location"
QK_LOCATION_B = "dbp_location"

QK_AUTHOR = "dbo_author"
QK_AUTHOR = "dbo_author_birthName"

QK_MUS = "dbo_museum"
QK_MUS_NAME = "foaf_museum_name"
QK_MUS_LAT = "geo_museum_lat"
QK_MUS_LNG = "geo_museum_lng"
QK_MUS_LATLNG = "georss_museum_point"
QK_MUS_LOCATION = "dbo_museum_location"
QK_MUS_LOCATION_B = "dbp_museum_location"

SPLITTER = "<~>"
UNKNOWN = "<unknown>"

import os


def dbpediaJSON_to_artwork_list(json_file_or_string, out_json_file=None, doGpsToAddressQuery=False):
    if os.path.isfile(json_file_or_string):
        json_str = open(json_file_or_string).read()
    else:
        json_str = json_file_or_string
    jdata = json.loads(json_str)

    keeplist = ListRefactor(list_rule=ListRule.keep_list,
                            one_element_rule=OneElementListRule.follow_list_rule,
                            bad_rule=BadOrNoneInListRule.remove,
                            empty_rule=EmptyListRule.none_value,
                            bad_value=u"")

    pickfirst = ListRefactor(list_rule=ListRule.first_value,
                             one_element_rule=OneElementListRule.follow_list_rule,
                             bad_rule=BadOrNoneInListRule.remove,
                             empty_rule=EmptyListRule.none_value,
                             bad_value=u"")

    concatparag = ListRefactor(list_rule=ListRule.reduce_value,
                               one_element_rule=OneElementListRule.follow_list_rule,
                               bad_rule=BadOrNoneInListRule.remove,
                               empty_rule=EmptyListRule.none_value,
                               list_reducer_func=lambda x, y: str(x) + "\n\n" + str(y),
                               bad_value=u"")

    # concatlist = ListRefactor(list_rule=ListRule.reduce_value,
    #                           one_element_rule=OneElementListRule.follow_list_rule,
    #                           bad_rule=BadOrNoneInListRule.remove,
    #                           empty_rule=EmptyListRule.none_value,
    #                           list_reducer_func=lambda x, y: str(x) + ", " + str(y))

    # avg = ListRefactor(list_rule=ListRule.reduce_value,
    #                    one_element_rule=OneElementListRule.follow_list_rule,
    #                    bad_rule=BadOrNoneInListRule.remove,
    #                    empty_rule=EmptyListRule.none_value,
    #                    list_reducer_func=lambda x, y: avg(float(x), float(y)))

    artworkList = []

    for r in jdata:
        artwork = Artwork()

        # out = r["artwork"]["value"]
        # data = dict()


        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get artwork name, artist name, ...                                                                           *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        artwork.uri = r[QK_ARTWORK] # this field is not optional!

        artwork.title = list_in_dict_refactor(r, QK_TITLE, pickfirst)

        mus = Museum()
        mus.uri = list_in_dict_refactor(r, QK_MUS, pickfirst)
        mus.name = list_in_dict_refactor(r, QK_MUS_NAME, pickfirst)
        if mus.uri is not None:
            artwork.addMuseum(mus)

        artwork.description = list_in_dict_refactor(r, QK_DESCRIPTION, concatparag)
        artwork.comment = list_in_dict_refactor(r, QK_COMMENT, concatparag)

        artwork.thumb_link = list_in_dict_refactor(r, QK_THUMB, pickfirst)
        artwork.img_link = list_in_dict_refactor(r, QK_IMG, pickfirst)

        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get GPS location of the artwork or, if not available, of the museum:                                         *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        #  ARTWORK GPS:
        if QK_LAT in r.keys() and QK_LNG in r.keys():
            artwork.currentLatLng.lat = list_in_dict_refactor(r, QK_LAT, pickfirst)
            artwork.currentLatLng.lng = list_in_dict_refactor(r, QK_LNG, pickfirst)

        elif QK_LATLNG in r.keys():
            i = 0
            lat_sum = 0
            lng_sum = 0
            list_of_latlng = list_in_dict_refactor(r, QK_LATLNG, keeplist)
            if list_of_latlng is not None:
                for ll in list_of_latlng:
                    latlng = ll.split(',')
                    lat_sum += float(latlng[0])
                    lng_sum += float(latlng[1])
                    i += 1
                if i > 0:
                    artwork.currentLatLng.lat = lat_sum / i
                    artwork.currentLatLng.lng = lng_sum / i

        # MUSEUM GPS:
        elif QK_MUS_LAT in r.keys() and QK_MUS_LNG in r.keys():
            artwork.currentLatLng.lat = list_in_dict_refactor(r, QK_MUS_LAT, pickfirst)
            artwork.currentLatLng.lat = list_in_dict_refactor(r, QK_MUS_LNG, pickfirst)

        elif QK_MUS_LATLNG in r.keys():
            i = 0
            lat_sum = 0
            lng_sum = 0
            list_of_latlng = list_in_dict_refactor(r, QK_MUS_LATLNG, keeplist)
            if list_of_latlng is not None:
                for ll in list_of_latlng:
                    latlng = ll.split(',')
                    lat_sum += float(latlng[0])
                    lng_sum += float(latlng[1])
                    i += 1
                if i > 0:
                    artwork.currentLatLng.lat = lat_sum / i
                    artwork.currentLatLng.lng = lng_sum / i
        else:
            artwork.currentLatLng.lat = None
            artwork.currentLatLng.lng = None
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get location (city name) from GPS or JSON data                                                               *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        address = None
        if (doGpsToAddressQuery and
                    gps_to_address == True and artwork.currentLatLng.lat != None and artwork.currentLatLng.lng != None):

            retry = True
            gotAddress = False
            while (retry):
                try:
                    time.sleep(GPS_SERVER_REQUEST_DELAY)
                    address = gpsToAddress(artwork.currentLatLng.lat, artwork.currentLatLng.lng)
                    if address != None:
                        retry = False
                        gotAddress = True
                    else:
                        print("\nNone address returned.")
                        ch = raw_input("\nTry again? [Y|n]\n> ")
                        if ch == "n" or ch == "N":
                            retry = False
                            gotAddress = False
                        else:
                            retry = True
                except GeocoderTimedOut as error:
                    retry = True
                except GeocoderServiceError as error:
                    if "429" in error.message:  # too many request error
                        if request_user_action_if_errror_429:
                            print("\nServer says too many request: " + error.message)
                            ch = raw_input("\nRetry to connect? [Y|n]\n> ")
                            if ch == "n" or ch == "N":
                                retry = False
                                return
                            else:
                                retry = True
                        else:
                            time.sleep(GPS_SERVER_REQUEST_DELAY_IF_ERROR_429)
                            retry = True
                    elif "Errno -2" in error.message:
                        print("\nCan't reach server: " + error.message)
                        ch = raw_input("\nRetry to connect? [Y|n]\n> ")
                        if ch == "n" or ch == "N":
                            retry = False
                            return
                        else:
                            retry = True
                    else:
                        print("\nServer unknown error: " + error.message)
                        ch = raw_input("\nRetry to connect? [Y|n]\n> ")
                        if ch == "n" or ch == "N":
                            retry = False
                            return
                        else:
                            retry = True

            if gotAddress:
                if address.city is not None:
                    artwork.currentLocations.append(address.city)
                elif address.county_province is not None:
                    artwork.currentLocations.append(address.county_province)
                elif address.state_region is not None:
                    artwork.currentLocations.append(address.state_region)
                elif address.country is not None:
                    artwork.currentLocations.append(address.country)
            else:
                address = None

        if address is None:
            lambda_locations_list = [list_in_dict_refactor(r, QK_MUS_LOCATION, keeplist),
                                     list_in_dict_refactor(r, QK_MUS_LOCATION, keeplist),
                                     list_in_dict_refactor(r, QK_LOCATION_B, keeplist),
                                     list_in_dict_refactor(r, QK_MUS_LOCATION_B, keeplist)]
            for locations in lambda_locations_list:
                if locations is not None:
                    artwork.currentLocations = []
                    for loc in locations:
                        artwork.currentLocations.append(loc)
                    break
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


        if print_gps_address_info:
            if address is None:
                print "-- address missing -- (no gps info)"
            else:
                print(address.toString())

        if print_location:
            if not artwork.currentLocations:
                print("<no-location>")
            else:
                for loc in artwork.currentLocations:
                    print(loc + "\t")

        if print_artwork:
            print vars(artwork)

        artworkList.append(artwork)

    if out_json_file is not None:
        json_str = json.dumps(todict(artworkList))
        json_file = open(out_json_file, "w")
        json_file.write(json_str)
        json_file.close()

    return artworkList




    #
    # artworkList = dbpediaJSON_to_artwork_list()
    # jsonStr = json.dumps(todict(artworkList))
    #
    # file = open(OUTPUT_FILE, "w")
    # file.write(jsonStr);
    # file.close()




    #  Procesor for the queries:
    # PREFIX owl: <http://www.w3.org/2002/07/owl#>
    # PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    # PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    # PREFIX dc: <http://purl.org/dc/elements/1.1/>
    # PREFIX : <http://dbpedia.org/resource/>
    # PREFIX dbpedia2: <http://dbpedia.org/property/>
    # PREFIX dbpedia: <http://dbpedia.org/>
    # PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    # PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    # PREFIX georess: <http://www.georss.org/georss/point>
    #
    #
    #
    # SELECT DISTINCT
    #
    # ?artwork
    # ?title
    # (GROUP_CONCAT(DISTINCT(?comment);separator=" <~> ") as ?comment)
    # (GROUP_CONCAT(DISTINCT(?description);separator=" <~> ") as ?description)
    #
    #
    # # (GROUP_CONCAT(DISTINCT(?lat);separator=" <~> ") as ?lat)
    # # (GROUP_CONCAT(DISTINCT(?lng);separator=" <~> ") as ?lng)
    # (AVG((?lat)) as ?lat)
    # (AVG((?lng)) as ?lng)
    # (GROUP_CONCAT(DISTINCT(?latlng);separator=" <~> ") as ?latlng)
    # (GROUP_CONCAT(DISTINCT(?location_a);separator=" <~> ") as ?location_a)
    # (GROUP_CONCAT(DISTINCT(?location_b);separator=" <~> ") as ?location_b)
    #
    #
    #
    #
    #
    # (GROUP_CONCAT(DISTINCT(?author);separator=" <~> ") as ?author)
    #
    # ?mus
    # #?mus_name
    #
    # (GROUP_CONCAT(DISTINCT(?mus_name );separator=" <~> ") as ?mus_name )
    #
    #
    # # (GROUP_CONCAT(DISTINCT(?mus_lat);separator=" <~> ") as ?mus_lat)
    # # (GROUP_CONCAT(DISTINCT(?mus_lng);separator=" <~> ") as ?mus_lng)
    # (AVG((?mus_lat)) as ?mus_lat)
    # (AVG((?mus_lng)) as ?mus_lng)
    # (GROUP_CONCAT(DISTINCT(?mus_latlng);separator=" <~> ") as ?mus_latlng)
    # (GROUP_CONCAT(DISTINCT(?mus_location_a);separator=" <~> ") as ?mus_location_a)
    # (GROUP_CONCAT(DISTINCT(?mus_location_b);separator=" <~> ") as ?mus_location_b)
    #
    #
    #
    # WHERE {
    #
    #   ?artwork   a                dbo:Artwork .
    #
    #   OPTIONAL { ?artwork   dbp:title        ?title } .
    #   OPTIONAL { ?artwork   rdfs:comment     ?comment } .
    #   OPTIONAL { ?artwork   dbo:abstract     ?description } .
    #   OPTIONAL { ?artwork   dbo:author       ?author .
    #              ?author    dbo:birthName    ?author_name .} .
    #
    #
    #   OPTIONAL { ?artwork   georss:point ?latlng }.
    #   OPTIONAL { ?artwork   geo:lat      ?lat }.
    #   OPTIONAL { ?artwork   geo:long     ?lng }.
    #   OPTIONAL { ?artwork   dbo:location ?location_a } .
    #   OPTIONAL { ?artwork   dbp:location ?location_b }.
    #
    #   OPTIONAL { ?artwork   dbo:museum       ?mus  .
    #       OPTIONAL { ?mus   dbo:location ?mus_location_a } .
    #       OPTIONAL { ?mus   dbp:location ?mus_location_b }.
    #
    #       OPTIONAL { ?mus   georss:point ?mus_latlng }.
    #       OPTIONAL { ?mus   geo:lat      ?mus_lat }.
    #       OPTIONAL { ?mus   geo:long     ?mus_lng }.
    #       OPTIONAL { ?mus   foaf:name    ?mus_name }.
    #    }
    #
    # #  ?mus    dbo:location     dbr:Florence .
    #
    #      FILTER (lang(?title) = 'en')
    #      FILTER (lang(?description) = 'en')
    #      FILTER (lang(?comment) = 'en')
    #
    # }
    # GROUP BY ?artwork ?title ?mus
    # order by ?title
    #
    # LIMIT 1000
    #
    #
    #
    #
    #
    #
