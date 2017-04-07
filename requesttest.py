import requests
import os
import xml.sax
from lxml import etree
from io import StringIO

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






url = "http://localhost:8080/processReferences"

# open pdf file

with open("grobid1.pdf", "rb") as f:
    x= requests.post(url, files={"input":f})

print(x.text)

parser2 = etree.XMLPullParser(tag="{}biblStruct".format(namespace))
parser2.feed(x.text)

for action, elem in parser2.read_events():
    for i in elem:
        if i.tag.replace(namespace,'') == "monogr":
            result = parseMonogr(i)
            print(result)

