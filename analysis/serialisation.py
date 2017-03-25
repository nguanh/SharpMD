from backend.ingester.difference_storage import *
import datetime
import pickle
import msgpack
import json
from pympler import asizeof
import timeit



def get_pub_dict(url_id=None, title=None, pages=None, note=None, doi=None, abstract= None, copyright = None,
                 date_published=None, volume= None, number = None):
    return{
        "url_id": url_id,
        "title":title,
        "pages": pages,
        "note": note,
        "doi": doi,
        "abstract": abstract,
        "copyright": copyright,
        "date_published": date_published,
        "volume": volume,
        "number": number,
    }



def generate_test_data(number):
    result = generate_diff_store(get_pub_dict(url_id=0, title="Hello World",
                                              date_published=1990-11-10))
    for i in range(1,number+1):
        added_values = get_pub_dict(url_id=i, title="Hello World"+str(i),
                                    date_published="1990-11-11",
                                    abstract="Test Text"+str(i),
                                    doi = str(i),
                                    note="Lorem Ipsum Dolor"+ str(i),
                                    pages="11{}-22{}".format(i,i),
                                    volume=str(i),
                                    number=str(i),
                                    copyright="Copyright"+ str(i))
        insert_diff_store(added_values, result)

    return result



raw_data =[
    generate_test_data(1),
    generate_test_data(5),
    generate_test_data(10),
    generate_test_data(30),
    generate_test_data(62),
]

size_data = [asizeof.asizeof(x) for x in raw_data]
print("Raw-size",size_data)


packed_pickle = [pickle.dumps(x) for x in raw_data]
packed_pickle_size =[asizeof.asizeof(pickle.dumps(x)) for x in raw_data]
print("Pickle",packed_pickle_size)


packed_json = [json.dumps(x) for x in raw_data]
packed_json_size =[asizeof.asizeof(json.dumps(x)) for x in raw_data]
print("JSON",packed_json_size)

packed_mp = [msgpack.packb(x) for x in raw_data]
packed_mp_size =[asizeof.asizeof(msgpack.packb(x)) for x in raw_data]
print("Msg Pack", packed_mp_size)


def pickle_stuff(index):
    return pickle.dumps(raw_data[index])

def json_stuff(index):
    return json.dumps(raw_data[index])

def msg_stuff(index):
    return msgpack.packb(raw_data[index])


def un_pickle_stuff(index):
    return pickle.loads(packed_pickle[index])

def un_json_stuff(index):
    return json.loads(packed_json[index])

def un_msg_stuff(index):
    return msgpack.unpackb(packed_mp[index])

result_packing = {
    "json":[],
    "pickle":[],
    "msgp":[],
}
for i in range(len(raw_data)):
    tp = timeit.Timer("pickle_stuff({})".format(i), "from analysis.serialisation import pickle_stuff")
    result_packing["pickle"].append(tp.timeit(number=10000))
    tj = timeit.Timer("json_stuff({})".format(i), "from analysis.serialisation import json_stuff")
    result_packing["json"].append(tj.timeit(number=10000))
    tm = timeit.Timer("msg_stuff({})".format(i), "from analysis.serialisation import msg_stuff")
    result_packing["msgp"].append(tm.timeit(number=10000))


result_unpacking = {
    "json":[],
    "pickle":[],
    "msgp":[],
}
for i in range(len(raw_data)):
    tp = timeit.Timer("un_pickle_stuff({})".format(i), "from analysis.serialisation import un_pickle_stuff")
    result_unpacking["pickle"].append(tp.timeit(number=10000))
    tj = timeit.Timer("un_json_stuff({})".format(i), "from analysis.serialisation import un_json_stuff")
    result_unpacking["json"].append(tj.timeit(number=10000))
    tm = timeit.Timer("un_msg_stuff({})".format(i), "from analysis.serialisation import un_msg_stuff")
    result_unpacking["msgp"].append(tm.timeit(number=10000))

print("PACKING")
print(result_packing)
print("UNPACKING")
print(result_unpacking)