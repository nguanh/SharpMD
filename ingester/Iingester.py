from abc import ABC, abstractmethod
from .exception import IIngester_Exception


class Iingester(ABC):
    def __init__(self, name):
        self.query = ""
        self.limit = None
        self.name = name

    def set_limit(self, limit):
        if limit is None:
            return
        if isinstance(limit, int):
            self.limit = limit
        else:
            raise IIngester_Exception("Invalid limit value")

        if limit < 1:
            raise IIngester_Exception("Invalid limit value")
        self.limit = limit

    def get_query(self):
        if self.query != "" and self.limit is not None:
            return self.query + " LIMIT "+str(self.limit)
        return self.query

    @abstractmethod
    def get_global_url(self):
        pass
    @abstractmethod
    def mapping_function(self, query_dataset):
        pass
    @abstractmethod
    def update_harvested(self):
        pass

    def get_name(self):
        return self.name

    @staticmethod
    def generate_empty_mapping():
        return {
            "local_url": "",
            "publication": {
                "url_id": None,
                "cluster_id": None,
                "differences": None,
                "title": None,  # for title and cluster name
                "pages": None,
                "note": None,
                "doi": None,
                "abstract": None,
                "copyright": None,
                "date_added": None,
                "date_published": None,
                "volume": None,
                "number": None,
                "study_field_ids": None,
                "author_ids": None,
                "type_ids": None,
                "keyword_ids": None,
                "pub_source_ids": None,

            },
            "pub_release": {
                "key": None,
                "series": None,
                "edition": None,
                "location": None,
                "publisher": None,
                "institution": None,
                "school": None,
                "address": None,
                "isbn": None,
                "howpublished": None,
                "book_title": None,
                "journal": None,
            },
            "authors": [],
            "study_fields": [],
            "types": None,
            "keywords": [],
        }

    @staticmethod
    def generate_author_mapping(original_name,parsed_name, website = None, contact = None, about = None,
                                modified = None, orcid_id = None):
        return{
            "original_name": original_name,
            "parsed_name": parsed_name,
            "website": website,
            "contact": contact,
            "about": about,
            "modified": modified,
            "orcid_id": orcid_id,
        }