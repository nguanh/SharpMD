import requests
import os
from lxml import etree
from requests.exceptions import ConnectionError
from weaver.exceptions import GrobidException
import logging
namespace ="{http://www.tei-c.org/ns/1.0}"
#TODO replace faulty äöü
# Ăź = ü
def nameDot(name):
    if len(name) == 1:
        name += "."
    return name

def parsePersName(element):
    lastname = ""
    firstname = ""
    middlename = ""
    if element[0].tag.replace(namespace,'') != "persName":
        return None
    for i in element[0]:
        if i.tag.replace(namespace,'') == "surname":
            lastname = i.text + " "
        elif i.tag.replace(namespace, '') == "forename" and i.get("type") == "first":
            firstname += nameDot(i.text)+" "
        elif i.tag.replace(namespace, '') == "forename":
            middlename += nameDot(i.text) + " "

    finalname="{} {} {}".format(firstname.strip(), middlename.strip(), lastname.strip())
    # replace double white space with single
    finalname= finalname.replace("  ", " ")
    return finalname


def parseMonogr(element):
    result ={
        "title": None,
        "pubyear": None,
        "authors": []
    }
    for i in element:
        if i.tag.replace(namespace,'') == "title":
            result["title"] = i.text

        if i.tag.replace(namespace, '') == "imprint":
            for el in i:
                if el.tag.replace(namespace, '')== "date":
                    result["pubyear"]= el.get("when")
        if i.tag.replace(namespace, '') == "author":
            result["authors"].append(parsePersName(i))

    return result


def get_reference(tei_doc):
    """
    http://teibyexample.org/examples/TBED03v00.htm?target=biblStruct
    if analytic is defined, get title, year and author from it as it represents the smallest unit
    otherwise use monogr
    :param tei_doc:
    :return:
    """
    reference = {}
    monogr = tei_doc["monogr"]
    if "analytic" in tei_doc:
        analytic = tei_doc["analytic"]
        reference["title"] = tei_doc["analytic"]["title"]
        reference["pubyear"] = analytic["pubyear"] or monogr["pubyear"]
        reference["authors"] = analytic["authors"]
    else:
        reference = monogr

    # validate for existing title and authors
    if not  len(reference["authors"]) or  not reference["title"]:
        return None
    return reference


def grobid_queue(grobid_url, input_path, output_path,logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
    if os.path.isdir(input_path) is False:
        raise GrobidException("Invalid input path")
    try:
        requests.post(grobid_url)
    except ConnectionError:
        raise GrobidException("Grobid does not answer")

    #iterate over all pdf files
    for filename in os.listdir(input_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(input_path, filename)
            with open(file_path, "rb") as f:
                ref_handler = requests.post(grobid_url, files={"input": f})
            if ref_handler.ok is False:
                continue
            parser2 = etree.XMLPullParser(tag="{}biblStruct".format(namespace),load_dtd=True)
            parser2.feed(ref_handler.text)
            result = {}
            for action, elem in parser2.read_events():
                for i in elem:
                    if i.tag.replace(namespace, '') == "monogr":
                        result["monogr"] = parseMonogr(i)
                    if i.tag.replace(namespace, '') == "analytic":
                        result["analytic"] = parseMonogr(i)
                logger.debug("Original : %s", result)
                logger.debug("Reference: %s", get_reference(result))
                #TODO create reference document





grobid_queue("http://localhost:8080/processReferences","C:\\Users\\anhtu\\Google Drive\\Informatik 2016\\Test","")