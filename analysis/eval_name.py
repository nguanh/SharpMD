import os
import pymysql

import pandas
from ingester.helper import normalize_authors,calculate_author_similarity
from metaphone import doublemetaphone
from mysqlWrapper.mariadb import MariaDb
from ingester.helper import get_search_query
local_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(local_path,'data')

DB_NAME= "names"


def default_func(name,):
    return name


def metaphone(normal_name):
    name_list = []
    base_list = normal_name.split(" ")
    for subname in base_list:
        metaphone, tmp = doublemetaphone(subname)
        name_list.append(metaphone)

    return " ".join(name_list)


def start(attribute,transformation_function=default_func):
    authors = pandas.read_csv(os.path.join(file_path, "Author.csv"), index_col="Id")
    read_connector = pymysql.connect(user="root",
                                     password="master",
                                     host="localhost",
                                     charset="utf8mb4")
    counter = 0
    result_id = pandas.Series([])
    result_names = pandas.Series([])
    with read_connector.cursor() as cursor:
        for key, value in authors.iterrows():

            name = str(value['Name'])
            # transform name
            transformed_name = transformation_function(name)
            query = get_search_query(transformed_name)
            # generate search query
            SEARCH_QUERY = 'SELECT Id,{} FROM names.authorspapers WHERE MATCH({}) AGAINST (%s IN BOOLEAN MODE)'.format(
                attribute, attribute
            )
            # perform query
            cursor.execute(SEARCH_QUERY, (query,))

            matched = []
            for element in cursor:
                matched.append({
                    "id": element[0],
                    "name": element[1]
                })

            # apply algorithm
            similar = [obj for obj in matched if calculate_author_similarity(transformed_name, obj['name'])]
            # store ids as string
            id_list = ' '.join(str(x['id']) for x in similar if x['id'] != key)
            #name_list = ','.join(str(x['name']) for x in similar if x['name'] != transformed_name)

            result_id[key] =str(key) + " "+id_list
            #result_names[name] =str(transformed_name)+" "+ name_list

            counter += 1
            if counter % 5000 == 0:
                print(counter)

    result_id.to_csv(os.path.join(file_path,"test_id4.csv"))
    #result_names.to_csv(os.path.join(file_path, "test_names4.csv"))
    read_connector.close()



if __name__ =="__main__":
    start("normal_name",normalize_authors)
