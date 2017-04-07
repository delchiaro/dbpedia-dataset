import os
import shutil
from argparse import ArgumentParser

from artwork.artwork import ArtworkDataset
from dataset_filtering import artwork_dataset_filtering
from dbpediaJsonProcessing import dbpediaJSON_to_artwork_list
from sparqlQuery import *
from sparqlQuery.sparqlResultJsonRefactor import split_string_lists, remove_key_from_dict
from utils import todict

ENDPOINT = "http://dbpedia.org/sparql"
QUERY = "queries/query_big_noduplicate.txt"
DATASET_PATH = "./dataset/dataset_new/"

SPARQL_JSON_RESULT = "data/sparql_query_result.json"
SPARQL_JSON_RESULT_PROCESSED = "data/processing_result.json"

ARTWORK_DATASET = "data/artwork_dataset.json"
ARTWORK_DATASET_FILTERED = "data/artwork_dataset_filtered.json"



EXECUTE_QUERY = False
EXECUTE_PROCESSING = False
MAKE_IMAGE_DATASET = False

EXECUTE_GPS_TO_ADDRESS = False

DOWNLOAD_IMAGES = True

FLICKR = True
DBPEDIA = True
GOOGLE = True


SPLITTER_SYMBOL = " <~> "


def main(sparql_query=False, json_processing=False, make_artwork_dataset=False, filter_artwork_dataset=False,
         gps_request_in_dataset=False, dbpedia=False, dbpedia_width=800, google=0, flickr=0,
         sleep_between_artwork_download=0.5):

    if sparql_query:
        sparqlQueryJson(QUERY, output_json_file_path=SPARQL_JSON_RESULT, endpoint=ENDPOINT, offset_limit=1000)
        print "Query executed!"

    if json_processing:
        split_string_lists(SPARQL_JSON_RESULT, splitter_symbol=SPLITTER_SYMBOL, output_json_path=SPARQL_JSON_RESULT_PROCESSED)
        remove_key_from_dict(SPARQL_JSON_RESULT_PROCESSED, "value", ["type"], output_json_path=SPARQL_JSON_RESULT_PROCESSED)
        print "Conversion done!"


    if make_artwork_dataset:
        dbpediaJSON_to_artwork_list(json_file_or_string=SPARQL_JSON_RESULT_PROCESSED,
                                    out_json_file=ARTWORK_DATASET,
                                    doGpsToAddressQuery=gps_request_in_dataset)

    if filter_artwork_dataset:
        artwork_dataset = ArtworkDataset().loadJson(ARTWORK_DATASET)
        filtered_dataset = artwork_dataset_filtering(artwork_dataset)
        filtered_dataset.saveJson(ARTWORK_DATASET_FILTERED)


    if dbpedia or google>0 or flickr>0:

        ad = ArtworkDataset(img_path=DATASET_PATH)
        ad.loadJson(ARTWORK_DATASET)

        if dbpedia:
            ad.downloadDbPediaThumbs(preferred_dim=dbpedia_width, sleep_between_artwork=sleep_between_artwork_download)

        if google>0:
            ad.downloadGoogleImages(images_per_artwork=google, sleep_between_artwork=sleep_between_artwork_download,
                                    google_localization=".it")

        if flickr>0:
            ad.downloadFlickrImages(api_key="flickr.apikey", images_per_artwork=flickr, sleep_between_artwork=sleep_between_artwork_download)


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("-sparql", "--sparql-query", action='store_const', const=True, dest='sparql_query', default=False,
                        help="Execute sparql query to dbPedia, output file: " + SPARQL_JSON_RESULT)

    parser.add_argument("-proc", "--processing", action='store_const', const=True, dest='processing', default=False,
                        help="Execute the processing on the sparql_query response, output file: " + SPARQL_JSON_RESULT_PROCESSED)

    parser.add_argument("-make", "--make-dataset", action='store_const', const=True, dest='make_artwork_dataset', default=False,
                        help="Make the artwork dataset from the processed sparql response, output file: " + ARTWORK_DATASET)

    parser.add_argument("-filter", "--filter-dataset", action='store_const', const=True, dest='filter_artwork_dataset',
                        default=False,
                        help="Filter the image json dataset removing artworks with empty title or emprty description")

    parser.add_argument("-gps", "--gps-request", action='store_const', const=True, dest='gps_request_in_dataset', default=False,
                        help="Execute query to retrive location from gps information while making the dataset")


    parser.add_argument("-dbpedia", "--dbpedia-images", action='store_const', const=True, dest='dbpedia', default=False,
                        help="Execute image download")


    parser.add_argument("-sleep", "--sleep-time", action='store', dest='sleep_time', default=0.5, type=float,
                        help="Specify the number of seconds to sleep between the download of an artwork images and the next artwork images")


    parser.add_argument("-w", "--dbpedia-width", action='store', dest='dbpedia_width', default=800,
                        help="Specify the preferred width for the images downloaded from dbpedia")

    parser.add_argument("-google", "--google-images", action='store', dest='google', default=0, type=int,
                        help="Download the specified number of images from google, for each artwork in dataset.")

    parser.add_argument("-flickr", "--flickr-images", action='store', dest='flickr', default=0, type=int,
                        help="Download the specified number of images from google, for each artwork in dataset.")

    args=parser.parse_args()


    if not ( args.sparql_query or args.processing or args.make_img_dataset or
                 args.gps_request_in_dataset or args.dbpedia or args.google or args.flickr):
        parser.print_usage()

    main(sparql_query=args.sparql_query,
         json_processing=args.processing,
         make_artwork_dataset=args.make_artwork_dataset,
         filter_artwork_dataset=args.filter_artwork_dataset,
         gps_request_in_dataset=args.gps_request_in_dataset,

         dbpedia=args.dbpedia,
         dbpedia_width=args.dbpedia_width,
         google=args.google,
         flickr=args.flickr,
         sleep_between_artwork_download=args.sleep_time)

