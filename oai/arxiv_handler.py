from sickle.models import Record,Header
from datetime import datetime
#TODO add suffix for authors
class ArXivRecord(Record):

    def __init__(self, record_element, strip_ns=True):
        super(Record, self).__init__(record_element, strip_ns=strip_ns)
        self.header = Header(self.xml.find(
            './/' + self._oai_namespace + 'header'))
        self.deleted = self.header.deleted
        self.metadata = {}
        tree = self.xml.find(".//" + self._oai_namespace + "metadata/{http://arxiv.org/OAI/arXiv/}arXiv")
        if self.deleted is False and tree is not None:

            for element in tree.getchildren():
                # remove namespace from tag
                tag = element.tag.replace("{http://arxiv.org/OAI/arXiv/}", "")
                text = element.text
                if tag == "authors":
                    text = self.parse_authors(element)
                elif tag == "created" or tag == "updated":
                    text = datetime.strptime(text, "%Y-%m-%d")
                elif tag == "title":
                    text = text.strip()
                elif tag == "id":
                    # rename
                    tag = "identifier"

                self.metadata[tag] = text
            self.metadata["mdate"] = datetime.strptime(self.header.datestamp, "%Y-%m-%d")

    def parse_authors(self, element):
        result = ""
        for author in element.getchildren():
            if author.tag == "{http://arxiv.org/OAI/arXiv/}author":
                name_dict = {}
                for names in author:
                    name_dict[names.tag.replace("{http://arxiv.org/OAI/arXiv/}", "")] = names.text
                if "forenames" in name_dict:
                    result += name_dict["keyname"]+"," + name_dict["forenames"] + ";"
                else:
                    result += name_dict["keyname"] + ";"
        return result

    def __iter__(self):
        return iter(self.metadata.items())


ATTRIBUTE_ORDER = ["identifier", "created", "updated", "authors", "title", "msc-class", "acm-class",
                   "report-no", "journal-ref", "comments", "abstract", "categories", "doi", "mdate"]


def parse_arxiv(metadata):
    tup = ()
    for attribute in ATTRIBUTE_ORDER:
        if attribute not in metadata:
            tup += (None,)
        else:
            tup += (metadata[attribute],)
    return tup
