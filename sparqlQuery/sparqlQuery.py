from SPARQLWrapper import SPARQLWrapper, JSON
import json
import os

from utils import string_or_path


def sparqlQuery(myQuery, endpoint ="http://dbpedia.org/sparql", offset_limit = 1000):
    """
    :param myQuery: sparql string query
    :param endpoint: sparql endpoint
    :param offset_limit: offset of the query (the query should not have the OFFSET keyword)
    :return: result, keys
    """
    totalResult = []
    keys = []
    sparql = SPARQLWrapper(endpoint)
    stop=False
    i=0

    myQuery = string_or_path(myQuery)

    while stop==False:
        query = myQuery + "\nLIMIT " + str(offset_limit) + "\nOFFSET "+ str(i*offset_limit)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        c = sparql.query().convert()
        keys = c["head"]["vars"]
        result = c["results"]["bindings"]
        totalResult += result
        if len(result) == 0:
            stop=True
        i+=1
    return totalResult, keys


def sparqlQueryJson(sparql_query_or_file_path, endpoint, output_json_file_path = None, offset_limit=1000):
    # type: (str, str) -> (str, str)
    """
    :param sparql_query_or_file_path: sparql string query or path to txt file containing the query
    :param endpoint: sparql endpoint
    :param offset_limit: offset of the query (the query should not have the OFFSET keyword)
    :return: json_result, keys
    """

    query = string_or_path(sparql_query_or_file_path)

    result, keys = sparqlQuery(query, endpoint=endpoint, offset_limit=offset_limit)
    json_str = json.dumps(result)

    if output_json_file_path is not None:
        json_file = open(output_json_file_path, "w")
        json_file.write(json_str)

    return json_str, keys



# sparqlQueryToJsonFile("query_big_noduplicate.txt", endpoint ="http://dbpedia.org/sparql", offset_limit=1000 )