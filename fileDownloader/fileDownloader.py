import urllib.request
import os
from urllib.parse import urlparse
from os.path import basename


url1 = 'http://dblp.uni-trier.de/xml/dblp.xml.gz'
url2 = 'http://dblp.uni-trier.de/xml/dblp.dtd'
url3 = 'http://dblp.uni-trier.de/xml/docu/Person.java'


def progress_bar(blocks_transferred, block_size, total_size, output = False):
    """
    Function for displaying progress on currently downloaded file
    :param blocks_transferred:
    :param block_size:
    :param total_size:
    :return:
    """
    currentPercentage = min((blocks_transferred*block_size)*100//total_size,100)
    previousPercentage = 0
    if blocks_transferred > 0:
        previousPercentage = ((blocks_transferred-1)*block_size)*100//total_size

    # only print progress if percentage value has changed
    if currentPercentage-previousPercentage > 0:
        if output:
            print("{}% downloaded".format(currentPercentage))


def download_file(file_url, storage_path):
    """
    :param file_url:
    :param storage_path:
    :return:
    """
    # check path
    if os.path.isdir(storage_path) is False:
        raise Exception("Invalid Path")

    disassembled = urlparse(file_url)
    filename = basename(disassembled.path)
    # get files name from url
    file_path = storage_path + filename


    try:
        local_filename, headers = urllib.request.urlretrieve(file_url, file_path, reporthook=progress_bar)
    except ValueError:
        raise Exception("Invalid URL")

    else:
        return local_filename



