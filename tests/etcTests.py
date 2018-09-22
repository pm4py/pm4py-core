import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.evaluation.precision import factory as etc_factory
from pm4py.algo.discovery.inductive.versions import dfg_only


class ETCTest(unittest.TestCase):
    def test_etc1(self):
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = dfg_only.apply(log, None)
        precision = etc_factory.apply(log, net, marking, final_marking)

if __name__ == "__main__":
    unittest.main()