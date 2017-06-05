import datetime
import os
from lxml import etree
from dblp.helper import parse_mdate, parse_year, parse_title
import pandas
import matplotlib.pyplot as plt

COMPLETE_TAG_LIST = ("proceedings", "book")


def parse_xml(xmlPath, dtdPath, tagList=COMPLETE_TAG_LIST):
    # init values
    success_count = 0
    overall_count = 0
    etree.DTD(file=dtdPath)

    book_year = {}
    proceeding_year = {}


    # iterate through XML
    for event, element in etree.iterparse(xmlPath, tag=tagList, load_dtd=True):
        try:
            dataset = {
                'key': element.get('key'),
                'mdate': parse_mdate(element.get('mdate')),
                'type': element.tag
            }
        except:
            # skip dataset if invalid
            continue

        overall_count += 1

        # iterate through elements of block
        try:
            for child in element:
                if child.tag == 'year':
                    dataset[child.tag] = parse_year(child.text)
                if child.tag == 'title':
                    dataset[child.tag] = parse_title(child)
                if child.tag == ' publisher':
                    dataset[child.tag] = child.text
        except Exception as e:
            continue
        if dataset['type'] == "book":
            year = str(dataset['year'].year)
            if year in book_year:
                book_year[year] += 1
            else:
                book_year[year] = 1
        if dataset['type'] == "proceedings":
            year = str(dataset['year'].year)
            try:
                proceeding_year[year] += 1
            except KeyError:
                proceeding_year[year] = 1
        success_count += 1

        element.clear()

        if success_count % 10000 == 0:
            print(success_count)


    book_data = pandas.Series(book_year, name="Test")
    axis = book_data.plot()
    data2 = pandas.Series(proceeding_year, name="Proceedings")
    axis2 = data2.plot()
    plt.show()
    # https://stackoverflow.com/questions/22483588/how-can-i-plot-separate-pandas-dataframes-as-subplots
    return success_count


if __name__ =="__main__":
    local_path = os.path.dirname(os.path.abspath(__file__))
    parse_xml(os.path.join(local_path,"data\dblp.xml"),
              os.path.join(local_path,"data\dblp.dtd"))