import unittest
import os, sys, inspect
from pm4py.entities.log import util as log_util
from pm4py import util as pmutil

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir2)


class Classifiers1DocumentationTest(unittest.TestCase):
    def test_classifiers1documentation(self):
        from pm4py.entities.log.importer.xes import factory as xes_importer

        log = xes_importer.import_log(os.path.join("inputData","receipt.xes"))
        #print(log.classifiers)

        from pm4py.entities.log.util import insert_classifier

        log, activity_key = insert_classifier.insert_classifier_attribute(log, "Activity classifier")
        #print(activity_key)

        from pm4py.algo.discovery.alpha import factory as alpha_miner

        parameters = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY : activity_key}

        net, initial_marking, final_marking = alpha_miner.apply(log, parameters=parameters)

        from pm4py.entities.log.importer.xes import factory as xes_importer

        log = xes_importer.import_log(os.path.join("inputData","receipt.xes"))

        for trace in log:
            for event in trace:
                event["customClassifier"] = event["concept:name"] + event["lifecycle:transition"]

        from pm4py.algo.discovery.alpha import factory as alpha_miner

        parameters = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}

        net, initial_marking, final_marking = alpha_miner.apply(log, parameters=parameters)

if __name__ == "__main__":
    unittest.main()
