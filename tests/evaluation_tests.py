import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive.versions import dfg_only
from pm4py.evaluation.replay_fitness import factory as fitness_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.evaluation.simplicity import factory as simplicity_factory
from pm4py.evaluation import factory as evaluation_factory

class ProcessModelEvaluationTests(unittest.TestCase):
    def test_evaluation_pm1(self):
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = dfg_only.apply(log, None)
        fitness = fitness_factory.apply(log, net, marking, final_marking)
        precision = precision_factory.apply(log, net, marking, final_marking)
        generalization = generalization_factory.apply(log, net, marking, final_marking)
        simplicity = simplicity_factory.apply(net)

    def test_evaluation_pm2(self):
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = dfg_only.apply(log, None)
        metrics = evaluation_factory.apply(log, net, marking, final_marking)

if __name__ == "__main__":
    unittest.main()