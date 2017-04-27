import string
from unidecode import unidecode
from nameparser import HumanName
import re
from datetime import datetime
from enum import Enum
from many_stop_words import get_stop_words
punctuation_dict = str.maketrans({key: None for key in (string.punctuation)})
whitespace_dict = str.maketrans({key: None for key in (string.whitespace.replace(" ", ""))})
ascii_dict = str.maketrans({key: None for key in (string.printable)})

suffix_list = ["jr", "jnr", "sr", "snr"]
stop_word_list = get_stop_words("en")

# TODO regex for latex and html

def normalize_title(title, latex=False):

    # translate unicode characters to closest ascii characters
    ascii_decoded = unidecode(title)
    remove_punctuation = ascii_decoded.translate(punctuation_dict)
    remove_whitespace = remove_punctuation.translate(whitespace_dict)
    lowered = remove_whitespace.lower()
    only_one_space = lowered
    # by removing certain unicode characters we introduced multiple spaces, replace them by only on space
    while '  ' in only_one_space:
        only_one_space = only_one_space.replace('  ', ' ')

    return only_one_space.strip()


def normalize_authors(author):
    # split double names connected by - into separate names
    name_split = author.replace("-", " ")
    # translate unicode characters to closest ascii characters
    ascii_decoded = unidecode(name_split)
    remove_punctuation = ascii_decoded.translate(punctuation_dict)
    remove_whitespace = remove_punctuation.translate(whitespace_dict)
    lowered = remove_whitespace.lower()
    only_one_space = lowered
    # by removing certain unicode characters we introduced multiple spaces, replace them by only on space
    while '  ' in only_one_space:
        only_one_space = only_one_space.replace('  ', ' ')

    return only_one_space.strip()

def split_authors(author_csv):
    authors_list = author_csv.split(";")
    # remove last entry since its always empty
    del authors_list[-1]
    return authors_list


def get_name_block(author):
    # try to find last name
    num_names = len(author.split(" "))
    # if author name contains only one name, it will serve the purpose of the last name
    if num_names == 1:
        last_name = author
        result = normalize_title(last_name) + ","
    else:
        name = HumanName(author).as_dict()
        norm_last_name = normalize_title(name['last'])
        norm_first_name = normalize_title(name['first'])[0] if len(name['first']) > 0 else ''
        result = norm_last_name + "," + norm_first_name

    return result


def get_relevant_words(title, max_words=3):
    word_list = title.split(" ")
    sort_list = sorted(word_list, key=len)
    clean_list = []
    for word in reversed(sort_list):
        if word in stop_word_list:
            continue
        clean_list.append(word)
        if len(clean_list) >= max_words:
            break
    return clean_list


def get_search_query(title):

    word_list = get_relevant_words(title)
    search_query = ""
    invalid = 0
    for word in word_list:
        if len(word) < 4:
            invalid += 1
        search_query += "+{}* ".format(word)

    if invalid == len(word_list):
        return title

    return search_query.strip()



def parse_pages(pages, separator="-"):
    result = pages.split(separator)
    # publication contains only one page
    if len(result) == 1:
        return [result[0], result[0]]
    if len(result) == 2:
        return [result[0], result[1]]
    return [None, None]


class Status(Enum):
    SAFE = 0
    LIMBO = 1


class Match(Enum):
    NO_MATCH = 0
    SINGLE_MATCH = 1
    MULTI_MATCH = 2


class Reason(Enum):
    AMB_ALIAS = 0
    AMB_CLUSTER = 1
    AMB_PUB = 2
