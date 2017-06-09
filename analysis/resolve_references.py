import os
import pandas
import csv
import sys
import logging
local_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(local_path,"data")


def resolve(input_data, output):
    raw = pandas.read_csv(os.path.join(data_path, "count_ref.csv"), index_col='ID')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create the logging file handler
    fh = logging.FileHandler(output)
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)

    source_list = set()
    reference_list = set()
    for key,value in raw.iterrows():
        hex_source =('{:2x}'.format(value['source_paper'])).upper().zfill(8)
        hex_ref = ('{:2x}'.format(value['ref_paper'])).upper().zfill(8)
        source_list.add(hex_source)
        reference_list.add(hex_ref)

    # receive non duplicate list
    with open(input_data, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in spamreader:
            idx = row[0]
            title = row[1]
            if idx in source_list:
                source_list.discard(idx)
                print("SOURCE {}:{}".format(idx,title))
                logger.info("SOURCE {}:{}".format(idx,title))
            if idx in reference_list:
                reference_list.discard(idx)
                print("REF {}:{}".format(idx,title))
                logger.info("REF {}:{}".format(idx,title))

            if len(source_list) == 0 and len(reference_list)== 0:
                break


if __name__ =="__main__":
    resolve(sys.argv[1],sys.argv[2])

