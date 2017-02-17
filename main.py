from sparqlQuery import sparqlQueryJson
from dbpediaSparqlQuery import dbpediaJSON_to_artwork_list
from sparqlQuery.sparqlResultJsonRefactor import split_string_lists, remove_key_from_dict, remove_empty_literals

ENDPOINT = "http://dbpedia.org/sparql"
QUERY = "dbpediaSparqlQuery/queries/query_big_noduplicate.txt"
RESULT = "result.json"
RESULT_PROCESSED = "result_processed.json"

EXECUTE_QUERY = False
EXECUTE_PROCESSING = True
EXECUTE_GPS_TO_ADDRESS = False

if EXECUTE_QUERY:
    json_result, keys = sparqlQueryJson(QUERY, output_json_file_path=RESULT, endpoint=ENDPOINT, offset_limit=1000)

if EXECUTE_PROCESSING:
    split_string_lists(RESULT, splitter_symbol=" <~> ", output_json_path=RESULT_PROCESSED)
    remove_key_from_dict(RESULT_PROCESSED, "value", ["type"], output_json_path=RESULT_PROCESSED)
    remove_empty_literals(RESULT_PROCESSED, RESULT_PROCESSED)
    # artworkList = dbpediaJSON_to_artwork_list(json_file_or_string=RESULT,
    #                                           out_json_file=RESULT_PROCESSED,
    #                                           doGpsToAddressQuery=EXECUTE_GPS_TO_ADDRESS)

