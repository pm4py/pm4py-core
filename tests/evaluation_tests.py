import os
import unittest

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.evaluation import algorithm as evaluation_alg
from pm4py.algo.evaluation.generalization import algorithm as generalization_alg
from pm4py.algo.evaluation.precision import algorithm as precision_alg
from pm4py.algo.evaluation.replay_fitness import algorithm as fitness_alg
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_alg
from pm4py.objects.log.importer.xes import importer as xes_importer
from tests.constants import INPUT_DATA_DIR


class ProcessModelEvaluationTests(unittest.TestCase):
    def test_evaluation_pm1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        fitness = fitness_alg.apply(log, net, marking, final_marking)
        precision = precision_alg.apply(log, net, marking, final_marking)
        generalization = generalization_alg.apply(log, net, marking, final_marking)
        simplicity = simplicity_alg.apply(net)
        del fitness
        del precision
        del generalization
        del simplicity

    def test_evaluation_pm2(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        metrics = evaluation_alg.apply(log, net, marking, final_marking)
        del metrics


if __name__ == "__main__":
    unittest.main()
