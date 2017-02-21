import os
import shutil
from argparse import ArgumentParser

from artwork.artwork import ArtworkDataset
from dbpediaJsonProcessing import dbpediaJSON_to_artwork_list
from sparqlQuery import *
from sparqlQuery.sparqlResultJsonRefactor import split_string_lists, remove_key_from_dict
from utils import todict

ENDPOINT = "http://dbpedia.org/sparql"
QUERY = "queries/query_big_noduplicate.txt"
DATASET_PATH = "./dataset"

RESULT = "sparql_query_result.json"
RESULT_PROCESSED = "processing_result.json"
RESULT_DATASET = "artwork_dataset.json"



EXECUTE_QUERY = False
EXECUTE_PROCESSING = False
MAKE_IMAGE_DATASET = False

EXECUTE_GPS_TO_ADDRESS = False

DOWNLOAD_IMAGES = True

FLICKR = True
DBPEDIA = True
GOOGLE = True


SPLITTER_SYMBOL = " <~> "


def main(sparql_query=False, processing=False, make_img_dataset=False, gps_request_in_dataset=False,
         download_images=False, dbpedia=False, google=False, flickr=False):

    if sparql_query:
        sparqlQueryJson(QUERY, output_json_file_path=RESULT, endpoint=ENDPOINT, offset_limit=1000)
        print "Query executed!"

    if processing:
        split_string_lists(RESULT, splitter_symbol=SPLITTER_SYMBOL, output_json_path=RESULT_PROCESSED)
        remove_key_from_dict(RESULT_PROCESSED, "value", ["type"], output_json_path=RESULT_PROCESSED)
        print "Conversion done!"




    if make_img_dataset:
        dbpediaJSON_to_artwork_list(json_file_or_string=RESULT_PROCESSED,
                                    out_json_file=RESULT_DATASET,
                                    doGpsToAddressQuery=gps_request_in_dataset)



    if download_images:

        ad = ArtworkDataset()
        ad.loadJson(RESULT_DATASET)

        if dbpedia:
            ad.downloadDbPediaThumbs(preferred_dim=800, sleep_between_artwork=2)

        if google:
            ad.downloadGoogleImages(images_per_artwork=4, sleep_between_artwork=2)

        if flickr:
            ad.downloadFlickrImages(api_key="flickr.apikey", images_per_artwork=6, sleep_between_artwork=2)


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-sparql", "--sparql-query", action='store_const', const=True, dest='sparql_query', default=False,
                        help="Execute sparql query to dbPedia, output file: " + RESULT )

    parser.add_argument("-proc", "--processing", action='store_const', const=True, dest='processing', default=False,
                        help="Execute the processing on the sparql_query response, output file: " + RESULT_PROCESSED)

    parser.add_argument("-make", "--make-dataset", action='store_const', const=True, dest='make_img_dataset', default=False,
                        help="Make the artwork dataset from the processed sparql response, output file: " + RESULT_DATASET)


    parser.add_argument("-gps", "--gps-request", action='store_const', const=True, dest='gps_request_in_dataset', default=False,
                        help="Execute query to retrive location from gps information while making the dataset")


    parser.add_argument("-dbpedia", "--dbpedia-images", action='store_const', const=True, dest='dbpedia', default=False,
                        help="Execute image download")

    parser.add_argument("-google", "--google-images", action='store_const', const=True, dest='google', default=False,
                        help="Execute image download")

    parser.add_argument("-flickr", "--flickr-images", action='store_const', const=True, dest='flickr', default=False,
                        help="Execute image download")

    args=parser.parse_args()


    if not ( args.sparql_query or args.processing or args.make_img_dataset or
                 args.gps_request_in_dataset or args.dbpedia or args.google or args.flickr):
        parser.print_usage()

    main(sparql_query=args.sparql_query,
         processing=args.processing,
         make_img_dataset=args.make_img_dataset,

         gps_request_in_dataset=args.gps_request_in_dataset,

         download_images=(args.dbpedia or args.google or args.flickr),
         dbpedia=args.dbpedia,
         google=args.google,
         flickr=args.flickr)

