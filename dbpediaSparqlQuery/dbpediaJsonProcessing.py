import json
import time
from enum import Enum

from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from gpsAddressQuery import gpsToAddress

from artworks.Artwork import Artwork, Museum

# Input
from utils import todict

DEFAULT_INPUT_FILE = "json/big_db.json"
OUTPUT_FILE = "json/big_db_organized_gpsConversion.json"

GPS_SERVER_REQUEST_DELAY = 4 # seconds delay for each request
GPS_SERVER_REQUEST_DELAY_IF_ERROR_429 = 1800

# Flags:
request_user_action_if_errror_429 = False
print_gps_address_info = True
print_location = False
print_artwork = False

gps_to_address = True # convert GPS informations (if available) to address

# Query Keys:
QK_ARTWORK      = "artwork"
QK_TITLE        = "dbp_title"
QK_LABEL        = "rdfs_label" #todo new
QK_NAME        = "foaf_name" #todo new
QK_THUMB       = "dbo_thumbnail" #todo new
QK_IMG         = "foaf_depiction" #todo new


QK_DESCRIPTION  = "dbo_abstract"
QK_COMMENT      = "rdfs_comment"

QK_LAT          = "geo_lat"
QK_LNG          = "geo_long"
QK_LATLNG       = "georss_point"
QK_LOCATION     = "dbo_location"
QK_LOCATION_B   = "dbp_location"

QK_AUTHOR = "dbo_author"
QK_AUTHOR = "dbo_author_birthName"

QK_MUS              = "dbo_museum"
QK_MUS_NAME         = "foaf_museum_name"
QK_MUS_LAT          = "geo_museum_lat"
QK_MUS_LNG          = "geo_museum_lng"
QK_MUS_LATLNG       = "georss_museum_point"
QK_MUS_LOCATION     = "dbo_museum_location"
QK_MUS_LOCATION_B   = "dbp_museum_location"


SPLITTER = "<~>"
UNKNOWN = "<unknown>"



import os

def dbpediaJSON_to_artwork_list(json_file_or_string, out_json_file = None, doGpsToAddressQuery = False):

    if os.path.isfile(json_file_or_string):
        json_str = open(json_file_or_string).read()
    else:
        json_str = json_file_or_string
    jdata = json.loads(json_str)

    artworkList = []

    for r in jdata:
        artwork = Artwork()

        out = r["artwork"]["value"]
        #data = dict()


        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get artwork name, artist name, ...                                                                           *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        artwork.uri = r[QK_ARTWORK]["value"] # this field is not optional!

        artwork.title = sparqlDictRefactor(r, QK_TITLE, ListConversion.pick_first)

        mus = Museum()
        mus.uri = sparqlDictRefactor(r, QK_MUS, ListConversion.pick_first)
        mus.name = sparqlDictRefactor(r, QK_MUS_NAME, ListConversion.pick_first)
        if mus.uri == None:
            mus = None
        artwork.addMuseum(mus)


        artwork.description = sparqlDictRefactor(r, QK_DESCRIPTION, ListConversion.concat, list_concat_spacer="\n\n")
        artwork.comment = sparqlDictRefactor(r, QK_COMMENT, ListConversion.concat, list_concat_spacer="\n\n")

        artwork.thumb_link = sparqlDictRefactor(r, QK_THUMB, ListConversion.pick_first)
        artwork.img_link = sparqlDictRefactor(r, QK_IMG, ListConversion.pick_first)


        if QK_TITLE in r.keys():
            artwork.title = r[QK_TITLE]["value"]
        if QK_MUS in r.keys():
            mus = None
            splitted = r[QK_MUS]["value"].split(SPLITTER)
            if len(splitted) >= 0:
                mus = Museum()
                mus.uri = splitted[0]

                if QK_MUS_NAME in r.keys():
                    splitted = r[QK_MUS_NAME]["value"].split(SPLITTER)
                    if splitted >= 0:
                        mus.name = splitted[0]

            if mus is not None:
                artwork.addMuseum(mus)
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *






        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get comment and descriptions from JSON data                                                                  *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        if QK_DESCRIPTION in r.keys() and r[QK_DESCRIPTION]["value"]:
            splitted = r[QK_DESCRIPTION]["value"].split(SPLITTER)
            for loc in splitted:
                artwork.description.append(loc)

        if QK_COMMENT in r.keys() and r[QK_COMMENT]["value"]:
            splitted = r[QK_COMMENT]["value"].split(SPLITTER)
            for loc in splitted:
                artwork.comment.append(loc)
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get thumbnail and image link from JSON data                                                                  *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        if QK_THUMB in r.keys() and r[QK_THUMB]["value"]:
            splitted = r[QK_THUMB]["value"].split(SPLITTER)
            for thumb in splitted:
                artwork.thumb_link = thumb

        if QK_IMG in r.keys() and r[QK_IMG]["value"]:
            img = r[QK_IMG]["value"].split(SPLITTER)
            for loc in splitted:
                artwork.img_link = img
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *






        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get GPS location of the artwork or, if not available, of the museum:                                         *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        #  ARTWORK GPS:
        if QK_LAT in r.keys() and QK_LNG in r.keys():
            artwork.currentLatLng.lat = r[QK_LAT]["value"]
            artwork.currentLatLng.lng = r[QK_LNG]["value"]
        elif QK_LATLNG in r.keys() and r[QK_LATLNG]["value"]:
            i=0
            lat_sum = 0
            lng_sum = 0
            splitted = r[QK_LATLNG]["value"].split(SPLITTER)
            for ll in splitted:
                latlng = ll.split()
                lat_sum += latlng[0]
                lng_sum += latlng[1]

            if(i>0):
                artwork.currentLatLng.lat=lat_sum/i
                artwork.currentLatLng.lng=lng_sum/i

        #MUSEUM GPS:
        elif QK_MUS_LAT in r.keys() and QK_MUS_LNG in r.keys():
            artwork.currentLatLng.lat = r[QK_MUS_LAT]["value"]
            artwork.currentLatLng.lng = r[QK_MUS_LNG]["value"]
        elif QK_MUS_LATLNG in r.keys() and r[QK_MUS_LATLNG]["value"]:
            i=0
            lat_sum = 0
            lng_sum = 0
            for ll in r[QK_MUS_LATLNG].split(SPLITTER):
                latlng = ll.split()
                lat_sum += latlng[0]
                lng_sum += latlng[1]

            if(i>0):
                artwork.currentLatLng.lat=lat_sum/i
                artwork.currentLatLng.lng=lng_sum/i

        # NO GPS FOUND:
        else:
            artwork.currentLatLng.lat = None
            artwork.currentLatLng.lng = None
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *






        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        # Try to get location (city name) from GPS or JSON data                                                               *
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        address = None
        if(doGpsToAddressQuery and
                   gps_to_address==True and artwork.currentLatLng.lat != None and artwork.currentLatLng.lng != None):

            retry = True
            gotAddress = False
            while(retry):
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
                    if "429" in error.message: # too many request error
                        if request_user_action_if_errror_429:
                            print( "\nServer says too many request: " + error.message )
                            ch = raw_input("\nRetry to connect? [Y|n]\n> ")
                            if ch == "n" or ch == "N":
                                retry = False
                                return
                            else: retry = True
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
                if address.city != None:
                    artwork.currentLocations.append(address.city)
                elif address.county_province != None:
                    artwork.currentLocations.append(address.county_province)
                elif address.state_region != None:
                    artwork.currentLocations.append(address.state_region)
                elif address.country != None:
                    artwork.currentLocations.append(address.country)
            else: address = None

        if address == None:
            if QK_LOCATION in r.keys() and r[QK_LOCATION]["value"]:
                splitted = r[QK_LOCATION]["value"].split(SPLITTER)
                for loc in splitted:
                    artwork.currentLocations.append( loc )

            elif QK_MUS_LOCATION in r.keys()  and r[QK_MUS_LOCATION]["value"]:
                splitted = r[QK_MUS_LOCATION]["value"].split(SPLITTER)
                for loc in splitted:
                    artwork.currentLocations.append( loc )

            elif QK_LOCATION_B in r.keys() and r[QK_LOCATION_B]["value"]:
                splitted = r[QK_LOCATION_B]["value"].split(SPLITTER)
                for loc in splitted:
                    artwork.currentLocations.append(loc)

            elif QK_MUS_LOCATION_B in r.keys() and r[QK_MUS_LOCATION_B]["value"]:
                splitted = r[QK_MUS_LOCATION_B]["value"].split(SPLITTER)
                for loc in splitted:
                    artwork.currentLocations.append(loc)
        # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


        if print_gps_address_info:
            if address == None:
                print "-- address missing -- (no gps info)"
            else: print(address.toString())

        if print_location:
            if not artwork.currentLocations:
                print("<no-location>")
            else:
                for loc in  artwork.currentLocations:
                    print(loc+"\t")

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