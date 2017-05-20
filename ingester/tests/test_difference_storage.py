#from unittest import TestCase
from django.test import TransactionTestCase
from ingester.difference_storage import *
from .ingester_tools import get_pub_dict
import datetime

import pickle
import msgpack
import json


class TestDifferenceStorage(TransactionTestCase):

    def test_generate_node1(self):
        self.assertIsNone(generate_node(None))

    def test_generate_node2(self):
        self.assertEqual(generate_node("hello"), {"value": "hello", "votes": 0, "bitvector": 1})

    def test_generate_node3(self):
        self.assertEqual(generate_node("hello",4), {"value": "hello", "votes": 0, "bitvector": 16})

    def test_generate_node4(self):
        self.assertEqual(generate_node(datetime.datetime(1990,1,1,1,1,1), 4), {"value": "1990-01-01 01:01:01",
                                                                               "votes": 0, "bitvector": 16})

    def test_generate_diff_store(self):
        result = generate_diff_store(get_pub_dict(url_id=5,title="Hello World",
                                                  date_published=datetime.datetime(1990,1,1,1,1,1)))
        self.assertEqual(result["url_id"],[5])
        self.assertEqual(result["title"],[ {"value": "Hello World","votes": 0, "bitvector": 1}])
        self.assertEqual(result["date_published"], [{"value": "1990-01-01 01:01:01", "votes": 0, "bitvector": 1}])
        self.assertEqual(result["abstract"],[])

    def test_insert_diff_store(self):
        result = generate_diff_store(get_pub_dict(url_id=5,title="Hello World",
                                                  date_published=datetime.datetime(1990,1,1,1,1,1)))
        added_values = get_pub_dict(url_id=2,title="Hello World", date_published=datetime.datetime(1990,2,2,2,2,2),
                                    abstract="Test Text")
        insert_diff_store(added_values,result)
        self.assertEqual(result["url_id"], [5,2])
        self.assertEqual(result["title"], [{"value": "Hello World", "votes": 0, "bitvector": 3}])
        self.assertEqual(result["date_published"],
                         [{"value": "1990-01-01 01:01:01", "votes": 0, "bitvector": 1},
                          {"value": "1990-02-02 02:02:02", "votes": 0, "bitvector": 2}
                          ])
        self.assertEqual(result["abstract"], [{"value": "Test Text", "votes": 0, "bitvector": 2}])

    def test_default_values(self):
        store = generate_diff_store(get_pub_dict(url_id=5,title="Hello World",
                                                  date_published=datetime.datetime(1990,1,1,1,1,1)))
        added_values = get_pub_dict(url_id=2,title="Hello World", date_published=datetime.datetime(1990,2,2,2,2,2),
                                    abstract="Test Text")
        insert_diff_store(added_values, store)

        result = get_default_values(store)
        self.assertDictEqual(result,{
            "title": "Hello World",
            "date_published":datetime.datetime(1990,1,1,1,1,1),
            "abstract": "Test Text",
            "note": None,
            "pages": None,
            "doi": None,
            "copyright": None,
            "volume": None,
            "number": None,

        })

    def test_serialize(self):
        store = generate_diff_store(get_pub_dict(url_id=5,title="Hello World (𝔹+)",
                                                  ))
        added_values = get_pub_dict(url_id=2,title="Hello World(𝔹+)", date_published=datetime.datetime(1990,2,2,2,2,2),
                                    abstract="Test Text")
        insert_diff_store(added_values,store)

        packed = serialize_diff_store(store)
        self.assertNotEqual(packed,store)
        unpacked = deserialize_diff_store(packed)
        self.assertEqual(unpacked,store)

    def test_msg_pack(self):
        result = generate_diff_store(get_pub_dict(url_id=5,title="Hello World (𝔹+)",
                                                  ))
        added_values = get_pub_dict(url_id=2,title="Hello World(𝔹+)", date_published=datetime.datetime(1990,2,2,2,2,2),
                                    abstract="Test Text")
        insert_diff_store(added_values,result)

        tmp = msgpack.packb(result)
        unpack = msgpack.unpackb(tmp, encoding="utf-8")
        self.assertEqual(result,unpack)

    def test_pickle(self):
        result = generate_diff_store(get_pub_dict(url_id=5,title="Hello World",
                                                  ))
        added_values = get_pub_dict(url_id=2,title="Hello World(𝔹+)",
                                    abstract="Test Text")
        insert_diff_store(added_values,result)
        tmp = pickle.dumps(result)
        self.assertEqual(result, pickle.loads(tmp))

    def test_json(self):
        result = generate_diff_store(get_pub_dict(url_id=5,title="Hello World (𝔹+)",
                                                  ))
        added_values = get_pub_dict(url_id=2,title="Hello World(𝔹+)",
                                    abstract="Test Text")
        insert_diff_store(added_values,result)
        tmp = json.dumps(result)
        self.assertEqual(result, json.loads(tmp))

    def test_url_indexes(self):
        bitvector = 5 # 101
        indices = get_url_indexes(bitvector)
        self.assertEqual(indices, [0,2])

    def test_get_url_1(self):
        global_url.objects.bulk_create(
            [
                global_url(id=111, domain="domain1", url="url1"),
                global_url(id=112, domain="domain2", url="url2"),
                global_url(id=113, domain="domain3", url="url3"),
            ]
        )
        local_url.objects.bulk_create([
            local_url(id=1, global_url_id=111, url="/lurl1"),
            local_url(id=2, global_url_id=112, url="/lurl2"),
            local_url(id=3, global_url_id=113, url="/lurl3"),
        ])
        store = generate_diff_store(get_pub_dict(url_id=1,title="Hello World",abstract="Common Text"))
        added_values1 = get_pub_dict(url_id=2,title="Hello World2",abstract="Unique Text")
        added_values2 = get_pub_dict(url_id=3,title="Hello World3",abstract="Common Text")
        insert_diff_store(added_values1,store)
        insert_diff_store(added_values2,store)

        result = get_sources(store)
        self.assertEqual(result[0], {
            "source": "url1/lurl1",
            "title": {
                "value": "Hello World",
                "votes": 0,
            },
            "abstract": {
                "value": "Common Text",
                "votes": 0,
            }
        }
        )
        self.assertEqual(result[1], {
            "source": "url2/lurl2",
            "title": {
                "value": "Hello World2",
                "votes": 0,
            },
            "abstract": {
                "value": "Unique Text",
                "votes": 0,
            }
        }
        )
        self.assertEqual(result[2], {
            "source": "url3/lurl3",
            "title": {
                "value": "Hello World3",
                "votes": 0,
            },
            "abstract": {
                "value": "Common Text",
                "votes": 0,
            }
        }
        )





