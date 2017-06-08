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
            if int(year) < 1990:
                element.clear()
                continue
            if int(year) >2016:
                element.clear()
                continue
            if year in book_year:
                book_year[year] += 1
            else:
                book_year[year] = 1
        if dataset['type'] == "proceedings":
            year = str(dataset['year'].year)
            if int(year) < 1990:
                element.clear()
                continue
            if int(year) >2016:
                element.clear()
                continue
            try:
                proceeding_year[year] += 1
            except KeyError:
                proceeding_year[year] = 1
        success_count += 1

        element.clear()

        if success_count % 10000 == 0:
            print(success_count)

    print(success_count)
    fig, axes = plt.subplots(nrows=1, ncols=2)
    book_data = pandas.Series(book_year, name="Journals")
    proceeding_data = pandas.Series(proceeding_year, name="Proceedings")
    axis = book_data.plot(ax=axes[0])
    axis2 = proceeding_data.plot(ax=axes[1])
    axis.set_ylim(0, 3000)
    axis2.set_ylim(0, 3000)
    axes[0].set_title('Journals')
    axes[1].set_title('Proceedings')

    plt.show()


if __name__ =="__main__":
    local_path = os.path.dirname(os.path.abspath(__file__))
    parse_xml(os.path.join(local_path,"data\dblp.xml"),
              os.path.join(local_path,"data\dblp.dtd"))