import os
import unittest

from pm4py import util as pmutil


class Classifiers1DocumentationTest(unittest.TestCase):
    def test_classifiers1documentation(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        from pm4py.objects.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "receipt.xes"))
        # print(log.classifiers)
        from pm4py.objects.log.util import insert_classifier
        log, activity_key = insert_classifier.insert_activity_classifier_attribute(log, "Activity classifier")
        # print(activity_key)
        from pm4py.algo.discovery.alpha import factory as alpha_miner
        parameters = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
        net, initial_marking, final_marking = alpha_miner.apply(log, parameters=parameters)
        del net
        del initial_marking
        del final_marking
        from pm4py.objects.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "receipt.xes"))
        for trace in log:
            for event in trace:
                event["customClassifier"] = event["concept:name"] + event["lifecycle:transition"]
        from pm4py.algo.discovery.alpha import factory as alpha_miner
        parameters = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}
        net, initial_marking, final_marking = alpha_miner.apply(log, parameters=parameters)
        del net
        del initial_marking
        del final_marking


if __name__ == "__main__":
    unittest.main()
