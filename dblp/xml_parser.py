import datetime
import os

from lxml import etree

from harvester.exception import IHarvest_Exception
from mysqlWrapper.mariadb import MariaDb
from .helper import parse_mdate, parse_year, dict_to_tuple, parse_title
from .queries import ADD_DBLP_ARTICLE
from time import time
COMPLETE_TAG_LIST = ("article", "inproceedings", "proceedings", "book", "incollection",
                     "phdthesis", "mastersthesis", "www", "person", "data")

TRACK_LIMIT = 500


def parse_xml(xmlPath, dtdPath, sql_connector, logger,
              tagList=COMPLETE_TAG_LIST, startDate=datetime.datetime.min, endDate=datetime.datetime.max, limit=None):
    """
    Function for parsing Dblp.xml file using lxml
    :param xmlPath: path to dblp.xml file
    :param dtdPath: path to dblp.dtd file
    :param sql_connector:
    :param tagList: tuple of tags we want to parse (inproceeedings,article,...) see DTD file
    :param startDate: include all records with mdate >= startDate
    :param endDate: include all records with mdate <= endDate
    :return: number of succesfully added records
    """
    # validate parameters
    if isinstance(tagList, (str, tuple)) is False:
        raise IHarvest_Exception("Invalid tagList")

    if os.path.isfile(xmlPath) is False:
        raise IHarvest_Exception("Invalid XML path")
    if os.path.isfile(dtdPath) is False:
        raise IHarvest_Exception("Invalid DTD path")
    if isinstance(sql_connector, MariaDb) is False:
        raise IHarvest_Exception("Invalid sql_connector instance")

    # init values
    success_count = 0
    overall_count = 0
    start_track = time()
    etree.DTD(file=dtdPath)
    sql_connector.set_query(ADD_DBLP_ARTICLE)
    if endDate is None:
        endDate = datetime.datetime.max
    if startDate is None:
        startDate = datetime.datetime.min

    # iterate through XML
    for event, element in etree.iterparse(xmlPath, tag=tagList, load_dtd=True):
        if limit is not None and overall_count >= limit:
            break
        if overall_count % TRACK_LIMIT == 0:
            start_track = time()

        try:
            dataset = {
                'key': element.get('key'),
                'mdate': parse_mdate(element.get('mdate')),
                'title': '',
                'type': element.tag
            }
        except:
            logger.error("%s invalid mdate", overall_count)
            # skip dataset if invalid
            continue

        # check date range
        if (startDate <= dataset["mdate"] <= endDate) is False:
                element.clear()
                continue
        overall_count += 1

        author_csv_list = ''

        # iterate through elements of block
        try:
            for child in element:
                if child.tag == 'author':
                    # stores authors as csv

                    author_csv_list += child.text + ";"
                elif child.tag == 'year':
                    dataset[child.tag] = parse_year(child.text)
                elif child.tag == 'title':
                    title = parse_title(child).replace('\n', '')
                    dataset[child.tag] = title
                else:
                    dataset[child.tag] = str(child.text).strip()
        except:
            logger.error("%s invalid year", dataset['key'])
            continue

        if author_csv_list == '':
            logger.debug("%s missing authors",dataset['key'])
            element.clear()
            continue
        if dataset['title'] == '':
            logger.error("%s missing title", dataset['key'])
            element.clear()
            continue
        dataset['author'] = author_csv_list

        tup = dict_to_tuple(dataset)
        element.clear()


        try:
            # include into database
            sql_connector.execute(tup)
        except Exception as e:
            logger.error("%s MariaDB error: %s",dataset['key'], e)
        else:
            success_count += 1
            logger.debug("%s: %s", success_count,element.get('key'))

        if overall_count % TRACK_LIMIT == 0:
            end_track = time()
            logger.info("TRACK:{}".format(end_track-start_track))
            start_track = time()

        if success_count % 10000 == 0:
            logger.info(success_count)

    logger.info("Final Count %s/%s", success_count, overall_count)
    sql_connector.close_connection()
    return success_count
