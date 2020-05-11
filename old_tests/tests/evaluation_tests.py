import os
import unittest

from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.evaluation import factory as evaluation_factory
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.replay_fitness import factory as fitness_factory
from pm4py.evaluation.simplicity import factory as simplicity_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.constants import INPUT_DATA_DIR


class ProcessModelEvaluationTests(unittest.TestCase):
    def test_evaluation_pm1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        fitness = fitness_factory.apply(log, net, marking, final_marking)
        precision = precision_factory.apply(log, net, marking, final_marking)
        generalization = generalization_factory.apply(log, net, marking, final_marking)
        simplicity = simplicity_factory.apply(net)
        del fitness
        del precision
        del generalization
        del simplicity

    def test_evaluation_pm2(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        metrics = evaluation_factory.apply(log, net, marking, final_marking)
        del metrics


if __name__ == "__main__":
    unittest.main()
