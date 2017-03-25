from datetime import datetime
from .exception import IHarvest_Exception


def is_empty_text(text):
    if text is None:
        return True
    if text == "\n":
        return True
    if len(text) == 0:
        return True
    return False


def parse_mdate(obj):
    """
    :param obj: string in format YYYY-MM-DD
    :return: datetime
    """
    try:
        return datetime.strptime(obj, "%Y-%m-%d")
    except:
        raise IHarvest_Exception('Invalid mdate')


def parse_year(obj):
    """
    :param obj: number containing publication year
    :return: date object, with month and day set to 1, as they are not further specified
    """
    try:
        year = int(obj)
        return datetime(year,1,1)
    except TypeError:
        raise IHarvest_Exception('year', 'Invalid year')
    except ValueError:
        raise IHarvest_Exception('year', 'Year is out of range')


def parse_title(root):

    text = ""
    if isinstance(root.text,str):
        text = root.text
    for child in root:
        if isinstance(child.text, str):
            text += child.text
        else:
            text += parse_title(child)

        if isinstance(child.tail, str):
            text += child.tail
        elif child.tail is not None:
            text += parse_title(child.tail)
    return text


def dict_to_tuple(obj):
    """
    attribute überprüfen, die zusätzlich existieren
    :param obj:
    :return:
    """
    all_attributes ={'key', 'mdate', 'author', 'title', 'ee', 'url', 'journal',
                     'number', 'volume', 'pages', 'year', "cite", "crossref", "booktitle",
                     "school", "address", "publisher", "isbn", "series", "type"}
    optional_attributes= ['ee', 'url', 'journal', 'number', 'volume', 'pages', "cite", "crossref", "booktitle", "year",
                          "school", "address", "publisher", "isbn", "series", "type"]

    # set missing attributes as None
    for attr in optional_attributes:
        if attr not in obj:
            obj[attr] = None

    if obj['title'] is None:
        print("title missing in", obj['key'])
        obj['title'] = "Test"


    result = (obj['key'],obj['mdate'], obj['author'], obj['title'], obj['pages'],
              obj['year'],obj['volume'], obj['journal'],obj['number'], obj['ee'],
              obj['url'], obj['cite'],obj['crossref'], obj['booktitle'],
              obj['school'],obj['address'],obj['publisher'],obj['isbn'],obj['series'],obj['type'],)
    return result