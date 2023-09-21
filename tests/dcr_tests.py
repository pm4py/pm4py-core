import os
import unittest

import pm4py
from pm4py.algo.discovery.dcr_discover import algorithm as alg
from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.dcr.exporter import exporter as dcr_exporter
from pm4py.objects.dcr.semantics import DcrSemantics
from pm4py.objects.conversion.dcr import *

class TestDcr(unittest.TestCase):

    #TODO: create a dict DCR graph and the same graph in the portal
    # it has to have: all relations + self relations + time

    def test_importer_from_portal(self):
        pass

    def test_exporter_to_xml_simple(self):
        pass

    def test_execution_semantics(self):
        pass

    def write_more_tests(self):
        pass