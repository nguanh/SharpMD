
from harvester.IHarvester import IHarvest
from harvester.exception import IHarvest_Exception, IHarvest_Disabled
from harvester.models import Schedule, IntervalSchedule,PeriodicTask,Config
from dblp.dblpharvester import DblpHarvester
from django.test import TestCase, mock



class TestIHarvest(TestCase):
    def setUp(self):
        # create IntervalSchedule
        self.config_id = 100
        self.interval, created = IntervalSchedule.objects.get_or_create(
                every = 10,
                period = IntervalSchedule.SECONDS)
        # create schedule
        self.schedule,created = Schedule.objects.get_or_create(
            name="test_schedule",
            time_interval= "all",
            schedule= self.interval,
        )

        # create periodic task
        self.periodic,created = PeriodicTask.objects.get_or_create(
            name="test",
            interval=self.interval,
            task="harvester.tasks.test"
        )

        self.config,created = Config.objects.get_or_create(
            id=self.config_id,
            name= "Test Harvester",
            table_name ="Test_Table",
            enabled = True,
            url="http://test.de/",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            schedule= self.schedule,
            extra_config={"zip_name": "dblp.xml.gz",
                          "dtd_name": "dblp.dtd",
                          "xml_name": "dblp.xml",
                          "extraction_path": "C:\\Users\\anhtu\\",
                          "tags":["a","b","c"]
                          }
        )

    def test_success(self):
        x = DblpHarvester(self.config_id)
        self.assertEqual(x.xml_url, "http://test.de/dblp.xml.gz")
        self.assertEqual(x.dtd_url, "http://test.de/dblp.dtd")
        self.assertEqual(x.xml_path, "C:\\Users\\anhtu\\dblp.xml")
        self.assertEqual(x.dtd_path, "C:\\Users\\anhtu\\dblp.dtd")
        self.assertEqual(x.tags, ("a","b","c"))

    def test_missing_xml(self):
        del self.config.extra_config["xml_name"]
        self.config.save()
        self.assertRaises(IHarvest_Exception,DblpHarvester,self.config_id)

    def test_missing_tags(self):
        del self.config.extra_config["tags"]
        self.config.save()
        self.assertRaises(IHarvest_Exception,DblpHarvester,self.config_id)

    def test_missing_extraction_path(self):
        del self.config.extra_config["extraction_path"]
        self.config.save()
        self.assertRaises(IHarvest_Exception,DblpHarvester,self.config_id)

    def test_invalid_extraction_path(self):
        self.config.extra_config["extraction_path"] = "blubbb"
        self.config.save()
        self.assertRaises(IHarvest_Exception, DblpHarvester, self.config_id)

    def test_invalid_tags(self):
        self.config.extra_config["tags"] = 5
        self.config.save()
        self.assertRaises(IHarvest_Exception, DblpHarvester, self.config_id)

    @mock.patch("dblp.dblpharvester.download_file", return_value = True)
    @mock.patch("dblp.dblpharvester.subprocess.call", return_value=0)
    def test_valid_init(self,func,func2):

        x = DblpHarvester(self.config_id)
        self.assertEqual(x.init(), True)

    def test_cleanup(self):
        x = DblpHarvester(self.config_id)
        x.cleanup()







