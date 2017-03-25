from unittest import TestCase
from harvester.IHarvester import IHarvest
from harvester.exception import IHarvest_Exception,IHarvest_Disabled
import logging
import datetime

class H1 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "xxx"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H2 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h1.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h2")
    def init(self):
        pass
    def run(self):
        pass

class H3 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h1.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H4 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h2.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H5 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h3.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H6 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h4.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H7 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h5.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass
class H8 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h6.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass
class H9 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h7.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass
class H10 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h8.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H12 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h9.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H13 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h10.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H14 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h11.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H15 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h12.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class H16 (IHarvest):
    def __init__(self):
        self.HARVESTER_PATH= "h13.ini"
        IHarvest.__init__(self, logging.getLogger("TEST"), "h1")
    def init(self):
        pass
    def run(self):
        pass

class TestIHarvest(TestCase):
    def test_h1(self):
        # invalid path
        self.assertRaises(IHarvest_Exception,H1)
    def test_h2(self):
        # invalid name
        self.assertRaises(IHarvest_Exception,H2)
    def test_h3(self):
        #no credentials
        self.assertRaises(IHarvest_Exception,H3)
    def test_h4(self):
        #missing username in credentials
        self.assertRaises(IHarvest_Exception,H4)
    def test_h5(self):
        #all valid
        H5()
    def test_h6(self):
        #missing enabled in ini
        self.assertRaises(IHarvest_Exception,H6)
    def test_h7(self):
        #enabled is false in ini
        self.assertRaises(IHarvest_Disabled,H7)
    def test_h8(self):
        #no limit is set, it is None
        x = H5()
        self.assertEqual(x.limit,None)
        self.assertEqual(x.start_date,None)
        self.assertEqual(x.end_date,None)

    def test_h9(self):
        #limit is valid
        x = H8()
        self.assertEqual(x.limit,100)
    def test_h10(self):
        #limit is negative, hence invalid
        self.assertRaises(IHarvest_Exception, H9)
    def test_h11(self):
        #limit is not int
        self.assertRaises(IHarvest_Exception, H10)

    def test_h12(self):
        #start and end dates not set, should be None both
        x = H12()
        self.assertEqual(x.start_date,None)
        self.assertEqual(x.end_date,None)

    def test_h13(self):
        #start date is invalid
        self.assertRaises(IHarvest_Exception,H13)

    def test_h14(self):
        #end date is invalid
        self.assertRaises(IHarvest_Exception,H14)

    def test_h15(self):
        #both values are valid
        x = H15()
        self.assertEqual(x.start_date, datetime.datetime(2011,10,1,0,0))
        self.assertEqual(x.end_date, datetime.datetime(2012, 4, 5, 0, 0))

    def test_h16(self):
        # end date is before start date
        self.assertRaises(IHarvest_Exception, H16)


