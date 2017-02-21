import os
import shutil

from artwork.artwork import ArtworkDataset
from dbpediaJsonProcessing import dbpediaJSON_to_artwork_list
from sparqlQuery import *
from sparqlQuery.sparqlResultJsonRefactor import split_string_lists, remove_key_from_dict
from utils import todict

ENDPOINT = "http://dbpedia.org/sparql"
QUERY = "queries/query_big_noduplicate.txt"
DATASET_PATH = "./dataset"

RESULT = "result.json"
RESULT_PROCESSED = "result_processed.json"
RESULT_DATASET = "artwork_dataset.json"



EXECUTE_QUERY = False
EXECUTE_PROCESSING = False
MAKE_IMAGE_DATASET = False

EXECUTE_GPS_TO_ADDRESS = False


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
                                              out_json_file=RESULT_DATASET,
                                              doGpsToAddressQuery=EXECUTE_GPS_TO_ADDRESS)


ad = ArtworkDataset()
ad.loadJson(RESULT_DATASET)
print "ciao"
