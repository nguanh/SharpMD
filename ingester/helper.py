import string
from unidecode import unidecode
from nameparser import HumanName
from enum import Enum
from many_stop_words import get_stop_words


from .author_names import AMBIGUOUS_NAMES
punctuation_dict = str.maketrans({key: None for key in (string.punctuation)})
whitespace_dict = str.maketrans({key: None for key in (string.whitespace.replace(" ", ""))})
ascii_dict = str.maketrans({key: None for key in (string.printable)})

suffix_list = ["jr", "jnr", "sr", "snr"]
stop_word_list = get_stop_words("en")

# TODO regex for latex and html

def normalize_title(title, latex=False):

    # translate unicode characters to closest ascii characters
    name_split = title.replace("-", " ")
    ascii_decoded = unidecode(name_split)
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
    name_split = name_split.replace(".", " ")
    # translate unicode characters to closest ascii characters
    ascii_decoded = unidecode(name_split)
    remove_punctuation = ascii_decoded.translate(punctuation_dict)
    remove_whitespace = remove_punctuation.translate(whitespace_dict)
    lowered = remove_whitespace.lower()
    only_one_space = lowered
    # by removing certain unicode characters we introduced multiple spaces, replace them by only on space
    while '  ' in only_one_space:
        only_one_space = only_one_space.replace('  ', ' ')

    word_list = [word if len(word) != 2 else word+"x" for word in only_one_space.split(" ")]
    combined_name = " ".join(word_list)

    return combined_name.strip()

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
        search_query += "{} ".format(word)

    if invalid == len(word_list):
        return title

    return search_query.strip()


def get_author_relevant_names(name):
    #normal_name = normalize_authors(name)
    name_list = name.split(" ")
    # get 3 longest name parts and remove abbreviations
    full_name_list = [n for n in name_list if len(n) > 1]

    sorted_list = sorted(full_name_list, key=len)
    return sorted_list


def get_author_search_query(name, max_length=3):
    name_list = get_author_relevant_names(name)
    search_query = ""
    valid = 0
    for word in reversed(name_list):
        if valid >= max_length:
            break
        search_query += "+{} ".format(word)
        if word not in AMBIGUOUS_NAMES:
            valid += 1

    return search_query.strip()


    # filter out ambiguous names


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
    AMB_NAME_BLOCK = 3

class Nameorder(Enum):
    WESTERN = 0
    ASIAN = 1



def calculate_author_similarity_tmp(orig_name, compare_name):
    orig_default = orig_name.split(" ")
    comp_default = compare_name.split(" ")

    #calculate scores
    score = get_name_score(orig_default)
    ALLOW_ABBREVIATIONS = False if score < 2 else True
    MAX_EXTRA_NAMES = score // 2

    potential_last_name = orig_default[-1]
    if len(potential_last_name) > 5:
        if potential_last_name not in comp_default:
            return False

    result1 = similarity_helper(orig_default, comp_default,MAX_EXTRA_NAMES, ALLOW_ABBREVIATIONS)
    result2 = similarity_helper(comp_default,orig_default,MAX_EXTRA_NAMES, ALLOW_ABBREVIATIONS)

    #heuristic: if last name has more than 5 characters it is probably not chinese--> use western order
    if result1 is True or result2 is True:
        return True


    # move last name to front
    orig_lshift = list_shift(orig_default,1,True)
    result3 = similarity_helper(orig_lshift, comp_default,MAX_EXTRA_NAMES, ALLOW_ABBREVIATIONS)
    result4 = similarity_helper(comp_default,orig_lshift,MAX_EXTRA_NAMES, ALLOW_ABBREVIATIONS)
    if result3 is True or result4 is True:
        return True

    # move first name to back
    orig_rshift = list_shift(orig_default,1,False)
    result5 = similarity_helper(orig_rshift, comp_default,MAX_EXTRA_NAMES, ALLOW_ABBREVIATIONS)
    result6 = similarity_helper(comp_default,orig_rshift,MAX_EXTRA_NAMES, ALLOW_ABBREVIATIONS)
    if result5 is True or result6 is True:
        return True

    return False



def list_shift(seq, n, right=True):
    if right is True:
        n = n % len(seq)
    else:
        n= (len(seq)-n) % len(seq)
    return seq[n:] + seq[:n]




def gen_helper(l):
    """
    generator to make a list loop continuable
    :param l:
    :return:
    """
    for element in l:
        yield element


def get_name_score(name_list):
    score = -1
    for name in name_list:
        if len(name) == 1:
            score += 0
        elif name in AMBIGUOUS_NAMES:
            score += 0
        elif len(name) <= 5:
            score += 1
        elif len(name) <= 8:
            score += 2
        else:
            score+= 3

    return score


def classify_order(name_list):
    total = len(name_list)
    sum = 0

    for name in name_list:
        if len(name) == 1:
            return Nameorder.WESTERN
        else:
            sum += len(name)

    if len(name_list[-1]) <=3:
        return Nameorder.ASIAN
    average = sum//total
    if average >= 4:
        return Nameorder.WESTERN

    return Nameorder.ASIAN


def calculate_author_similarity(orig_name, compare_name):

    orig_default = orig_name.split(" ")
    comp_default = compare_name.split(" ")
    if orig_default == comp_default:
        return True
    # try to classify original name
    name_order = classify_order(orig_default)
    if name_order == Nameorder.WESTERN:
        max_words = 1
        abbreviations = True
        orig_lshift = list_shift(orig_default, 1, False)
        comp_lshift = list_shift(comp_default, 1, False)
        # last names have to match
        if orig_lshift[0] != comp_lshift[0]:
            return False
        # first name have match, exactly or abbrviated
        if len(orig_lshift) < 2 or len(comp_lshift) < 2:
            return False
        # if first name is not equal
        if orig_lshift[1] != comp_lshift[1] and orig_lshift[1].startswith(comp_lshift[1]) is False and comp_lshift[1].startswith(orig_lshift[1]) is False:
            return False
        if orig_lshift[0] in AMBIGUOUS_NAMES:
            max_words = 0
            abbreviations = False

        return similarity_helper(orig_lshift, comp_lshift, max_words, abbreviations)
    elif name_order == Nameorder.ASIAN:
        # read names from left to right
        # allow
        orig_rshift = list_shift(orig_default, 1, True)
        orig_lshift = list_shift(orig_default, 1, False)


        result1 = similarity_helper(orig_default, comp_default,1, True)
        result2 = similarity_helper(comp_default, orig_default, 1, True)
        result3 = similarity_helper(orig_lshift, comp_default, 1, True)
        result4 = similarity_helper(comp_default, orig_lshift, 1, True)
        result5 = similarity_helper(orig_rshift, comp_default, 1, True)
        result6 = similarity_helper(comp_default, orig_rshift, 1, True)

        return result1 or result2 or result3 or result4 or result5 or result6


def similarity_helper(init_orig_list, init_comp_list, MAX_EXTRA_NAMES=1, ALLOW_ABBREVIATIONS=True):
    """

    :param init_orig_list: string list containing the original name
    :param init_comp_list:  string list containing the name it is compared with
    :param MAX_EXTRA_NAMES:  maximum number of deviating names
    :param ALLOW_ABBREVIATIONS:  allow abbreviation matching
    :return:
    """

    additional_names = False
    abbreviated_names = False
    orig_obj = [{"name": name, "match": None} for name in init_orig_list]
    comp_obj = [{"name": name, "match": None} for name in init_comp_list]
    comp_generator = gen_helper(comp_obj)
    for x in orig_obj:
        for y in comp_generator:
            if (x['name'] == y['name']) and (x['match'] is None and y['match'] is None):
                x["match"] = "EXACT_MATCH"
                y["match"] = "EXACT_MATCH"
                break;
            if ALLOW_ABBREVIATIONS:
                if len(x['name']) == 1 and y['name'].startswith(x['name']) and \
                                x['match'] is None and y['match'] is None:
                    x['match'] = "ABBR_FROM"
                    y['match'] = "ABBR_TO"
                    abbreviated_names = True
                    break
                    # y name is abbreviation from x name
                elif len(y['name']) == 1 and x['name'].startswith(y['name']) and \
                                y['match'] is None and x['match'] is None:
                    y['match'] = "ABBR_FROM"
                    x['match'] = "ABBR_TO"
                    abbreviated_names = True
                    break

    # step 3: evaluate results
    no_matches_orig = 0
    no_matches_comp = 0
    abbr_to_orig = 0
    abbr_from_orig = 0
    abbr_to_comp = 0
    abbr_from_comp = 0

    for element in orig_obj:
        # element has no match
        if element['match'] is None:
            no_matches_orig += 1
        elif element['match'] == "ABBR_FROM":
            abbr_from_orig += 1
        elif element['match'] == "ABBR_TO":
            abbr_to_orig += 1


    for element in comp_obj:
        # element has no match
        if element['match'] is None:
            no_matches_comp += 1
        elif element['match'] == "ABBR_FROM":
            abbr_from_comp += 1
        elif element['match'] == "ABBR_TO":
            abbr_to_comp += 1



    if abbr_from_orig > 0 and abbr_to_orig > 0:
        return False

    if abbr_from_comp > 0 and abbr_to_comp > 0:
        return False

    if no_matches_orig > 0 and no_matches_comp > 0:
        return False

    if no_matches_orig > MAX_EXTRA_NAMES or no_matches_comp > MAX_EXTRA_NAMES:
        return False

    if no_matches_orig > 0 or no_matches_comp > 0:
        additional_names = True


    if additional_names and abbreviated_names:
        return  False
    return True
