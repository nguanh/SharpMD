import requests
import os
import xml.sax
from lxml import etree
from io import StringIO
from http.client import HTTPConnection, HTTPException
namespace ="{http://www.tei-c.org/ns/1.0}"
#TODO replace faulty äöü
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
            lastname = i.text+ " "
        elif i.tag.replace(namespace, '') == "forename" and  i.get("type") == "first":
            firstname += nameDot(i.text) +" "
        elif i.tag.replace(namespace, '') == "forename" :
            middlename += nameDot(i.text) + " "

    finalname="{} {} {}".format(firstname.strip(),middlename.strip(),lastname.strip())
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
            if i[0].tag.replace(namespace, '')== "date":
                result["pubyear"]= i[0].get("when")
        if i.tag.replace(namespace, '') == "author":
            result["authors"].append(parsePersName(i))

    return result


class GrobidException(Exception):
    pass


def grobid_queue(grobid_url,input_path):
    if os.path.isdir(input_path) is False:
        raise GrobidException("Invalid input path")
    # TODO
    #if is_alive(grobid_url) is False:
        #raise(GrobidException("{} is not reachable".format(grobid_url)))

    #iterate over all pdf files
    for filename in os.listdir(input_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(input_path,filename)
            with open(file_path, "rb") as f:
                ref_handler = requests.post(grobid_url, files={"input": f})
            if ref_handler.ok is False:
                continue
            parser2 = etree.XMLPullParser(tag="{}biblStruct".format(namespace))
            parser2.feed(ref_handler.text)
            print(filename)
            """
            for action, elem in parser2.read_events():
                for i in elem:
                    if i.tag.replace(namespace, '') == "monogr":
                        try:
                            result = parseMonogr(i)
                            print(result)
                        except Exception as e:
                            print(e)
            """




grobid_queue("http://localhost:8080/processReferences","C:\\Users\\anhtu\\Google Drive\\Informatik 2016\\Related Work")