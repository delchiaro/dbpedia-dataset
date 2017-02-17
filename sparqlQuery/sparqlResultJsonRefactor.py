from enum import Enum
import json

from utils import string_or_path

DEFAULT_SPLITTER = " <~> "


def _split_string_lists(node, splitter_symbol=DEFAULT_SPLITTER, no_len_1_list=True):
    if isinstance(node, dict):
        new_node = {}
        for k in node.keys():
            new_node[k] = _split_string_lists(node[k], splitter_symbol)
        return new_node

    if isinstance(node, list):
        new_node = []
        for n in node:
            new_node.append(_split_string_lists(n, splitter_symbol))
        return new_node

    else:    # recursive end: not a list nor a dict
        if isinstance(node, str) or isinstance(node, unicode):
            splitted = node.split(splitter_symbol)
            if len(splitted) == 1 and no_len_1_list:
                return splitted[0]
            else:
                return splitted
        else:
            return node


def split_string_lists(input_json_or_path, splitter_symbol=DEFAULT_SPLITTER, output_json_path=None):
    # type: (str, str, str) -> str
    root = json.loads(string_or_path(input_json_or_path))
    new_root = _split_string_lists(root, splitter_symbol)

    json_str_processed = json.dumps(new_root)
    if output_json_path is not None:
        json_file = open(output_json_path, "w")
        json_file.write(json_str_processed)

    return new_root











def _remove_key_from_dict(node, key_to_extract, near_additional_keys=None):
    # type: (dict, str, list[str]) -> dict

    if isinstance(node, dict):

        all_near_keys_found = True
        if near_additional_keys is not None:
            for k in near_additional_keys:
                if k not in node.keys():
                    all_near_keys_found = False
                    break

        if all_near_keys_found and key_to_extract in node.keys():
            node = node[key_to_extract]

        if isinstance(node, dict):
            new_node = {}
            for k in node.keys():
                new_node[k] = _remove_key_from_dict(node[k], key_to_extract, near_additional_keys)

            return new_node
        else:
            return node

    if isinstance(node, list):
        new_node = []
        for n in node:
            new_node.append(_remove_key_from_dict(n, key_to_extract, near_additional_keys))
        return new_node

    else:    # recursive end: not a list nor a dict (leaf)
        return node


def remove_key_from_dict(input_json_or_path, key_to_extract, near_additional_keys=None, output_json_path=None):
    root = json.loads(string_or_path(input_json_or_path))
    new_root = _remove_key_from_dict(root, key_to_extract, near_additional_keys)
    json_str_processed = json.dumps(new_root)
    if output_json_path is not None:
        json_file = open(output_json_path, "w")
        json_file.write(json_str_processed)

    return new_root







# TODO: ftto così è inutile! None ritorna una stringa vuota in json. Verificare che convertendo da JSON a python la stringa vuota non torni un None, in tal caso eliminare questa funzione
def _remove_empty_literals(node):
    if isinstance(node, dict):
        new_node = {}
        for k in node.keys():
            new_node[k] = _split_string_lists(node[k])
        return new_node

    if isinstance(node, list):
        new_node = []
        for n in node:
            new_node.append(_split_string_lists(n))
        return new_node

    else:    # recursive end: not a list nor a dict
        if isinstance(node, str):
            if str == "":
                node = None

        elif isinstance(node, unicode):
            if str == u"":
                node = None
        return node


def remove_empty_literals(input_json_or_path, output_json_path=None):
    # type: (str, str, str) -> str
    root = json.loads(string_or_path(input_json_or_path))
    new_root = _remove_empty_literals(root)

    json_str_processed = json.dumps(new_root)
    if output_json_path is not None:
        json_file = open(output_json_path, "w")
        json_file.write(json_str_processed)

    return new_root





class ListConversion(Enum):
    keep_list = 0
    keep_list_if_multiple_values = 1
    pick_first = 2
    concat = 3


def listRefactor(string_with_list_splitter, list_splitter, list_conversion, list_concat_spacer="\n"):
    if len(string_with_list_splitter) <= 0:
        ret = None
    elif list_conversion == ListConversion.keep_list_if_multiple_values:
        if len(string_with_list_splitter) == 1:
            ret = string_with_list_splitter[0]
        else:
            ret = string_with_list_splitter
    elif list_conversion == ListConversion.keep_list:
        ret = string_with_list_splitter
    elif list_conversion == ListConversion.pick_first:
        ret = string_with_list_splitter[0]
    elif list_conversion == ListConversion.concat:
        ret = string_with_list_splitter[0]
        for d in string_with_list_splitter[1:]:
            ret += list_concat_spacer + d
    return ret


class SparqlValueType(Enum):
    uri = 0
    literal = 1


def sparqlDictRefactor(dictionary, key, list_conversion, list_concat_spacer="\n", only_sparql_type=None):
    # type: (dict, list, ListConversion, str) -> dict
    ret = None
    if key in dictionary.keys():
        if only_sparql_type is not None:
            if only_sparql_type == SparqlValueType.uri and dictionary[key]["type"] != "uri":
                return None
            if only_sparql_type == SparqlValueType.literal and dictionary[key]["type"] != "literal":
                return None

        if isinstance(dictionary[key], dict) and isinstance(dictionary[key]["value"], list):
            val_list = dictionary[key]["value"]
            ret = listRefactor(val_list, list_conversion, list_concat_spacer)
        else:
            ret = dictionary[key]["value"]
    return ret

