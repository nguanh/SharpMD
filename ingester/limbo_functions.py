from .models import *


def push_limbo(mapping, author_matching, title_reason):
    pub_dict = {
        "reason": title_reason,
        "url": mapping["local_url"],
        "title": mapping["publication"]["title"],
        "pages": mapping["publication"]["pages"],
        "note": mapping["publication"]["note"],
        "doi": mapping["publication"]["doi"],
        "abstract": mapping["publication"]["abstract"],
        "copyright": mapping["publication"]["copyright"],
        "date_added": mapping["publication"]["date_added"],
        "date_published": mapping["publication"]["date_published"],
        "volume": mapping["publication"]["volume"],
        "number": mapping["publication"]["number"],
        "series": mapping["pub_release"]["series"],
        "edition": mapping["pub_release"]["edition"],
        "location": mapping["pub_release"]["location"],
        "publisher": mapping["pub_release"]["publisher"],
        "institution": mapping["pub_release"]["institution"],
        "school": mapping["pub_release"]["school"],
        "address": mapping["pub_release"]["address"],
        "isbn": mapping["pub_release"]["isbn"],
        "howpublished": mapping["pub_release"]["howpublished"],
        "book_title": mapping["pub_release"]["book_title"],
        "journal": mapping["pub_release"]["journal"],
    }
    limbo = limbo_pub.objects.create(**pub_dict)
    for index, author in enumerate(mapping["authors"]):
        limbo_authors.objects.create(publication=limbo, name=author["original_name"], priority=index,
                                     reason=str(author_matching[index]["reason"]))
