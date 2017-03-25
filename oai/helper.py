
ATTRIBUTE_ORDER = ["identifier", "creator","title", "description",
                   "contributor","coverage", "date","format","language",
                   "publisher","relation", "rights","source", "subject","type"]


def parse_metadata_default(metadata):
    tup = ()
    for attribute in ATTRIBUTE_ORDER:
        if attribute not in metadata:
            tup += (None,)
        else:
            tup += (parse_entry(metadata[attribute]),)

    return tup


def parse_entry(obj):
    result = ""
    if isinstance(obj,list) is False:
        return obj
    else:
        for entry in obj:
            if entry is None:
                continue
            result += entry+ ";"
    return result.strip()