import os
import shutil

from dbpediaJsonProcessing import dbpediaJSON_to_artwork_list
from sparqlQuery import *
from sparqlQuery.sparqlResultJsonRefactor import split_string_lists, remove_key_from_dict
from utils import todict

ENDPOINT = "http://dbpedia.org/sparql"
QUERY = "dbpediaSparqlQuery/queries/query_big_noduplicate.txt"
RESULT = "result.json"
RESULT_PROCESSED = "result_processed.json"
DATASET_PATH = "./dataset"

EXECUTE_QUERY = False
EXECUTE_PROCESSING = True
EXECUTE_GPS_TO_ADDRESS = False
MAKE_IMAGE_DATASET = True

SPLITTER_SYMBOL = " <~> "

if EXECUTE_QUERY:
    json_result, keys = sparqlQueryJson(QUERY, output_json_file_path=RESULT, endpoint=ENDPOINT, offset_limit=1000)
    print "Query executed!"

if EXECUTE_PROCESSING:
    split_string_lists(RESULT, splitter_symbol=SPLITTER_SYMBOL, output_json_path=RESULT_PROCESSED)
    remove_key_from_dict(RESULT_PROCESSED, "value", ["type"], output_json_path=RESULT_PROCESSED)
    print "Conversion done!"




if MAKE_IMAGE_DATASET:
    artworkList = dbpediaJSON_to_artwork_list(json_file_or_string=RESULT_PROCESSED,
                                out_json_file=RESULT_PROCESSED,
                                doGpsToAddressQuery=EXECUTE_GPS_TO_ADDRESS)
    import urllib

    if os.path.isdir(DATASET_PATH):
        shutil.rmtree(DATASET_PATH)
    os.makedirs(DATASET_PATH)

    i = 0
    duplicati = []
    non_duplicati = []
    for artwork in artworkList:
        print i
        art_path = DATASET_PATH+"/" + (artwork.uri.replace("/", "\\"))
        if os.path.isdir(art_path):
            duplicati.append(artwork)

        else:
            non_duplicati = []
            os.makedirs(art_path)
            artwork_img_link = artwork.getThumbLink(500)
            if artwork_img_link is not None:
                filename = artwork.getAuthorName() + "-" + artwork.getTitle() + "-seed_w500.jpg"
                urllib.urlretrieve(urllib.unquote(artwork_img_link.encode('utf8', ':/')), art_path+"/" + filename)
        i+=1

    print "duplicati: " + str(len(duplicati))

    json_str = json.dumps(todict(duplicati))
    json_file = open("duplicati.json", "w")
    json_file.write(json_str)
    json_file.close()

    print "non duplicati: " + str(len(non_duplicati))

    json_str = json.dumps(todict(non_duplicati))
    json_file = open("dataset_non_duplicati.json", "w")
    json_file.write(json_str)
    json_file.close()