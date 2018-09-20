import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir2)


class DocMeasuresDocumentationTest(unittest.TestCase):
    def test_docmeasures11(self):
        from pm4py.entities.log.importer.xes import factory as xes_importer

        log = xes_importer.import_log(os.path.join("inputData", "receipt.xes"))

        from pm4py.algo.discovery.alpha import factory as alpha_miner
        from pm4py.algo.discovery.inductive import factory as inductive_miner

        alpha_petri, alpha_initial_marking, alpha_final_marking = alpha_miner.apply(log)
        inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)

        from pm4py.evaluation.replay_fitness import factory as replay_factory

        fitness_alpha = replay_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        fitness_inductive = replay_factory.apply(log, inductive_petri, inductive_initial_marking, inductive_final_marking)
        # print("fitness_alpha=",fitness_alpha)
        # print("fitness_inductive=",fitness_inductive)

        from pm4py.evaluation.precision import factory as precision_factory

        precision_alpha = precision_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        precision_inductive = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                      inductive_final_marking)

        # print("precision_alpha=",precision_alpha)
        # print("precision_inductive=",precision_inductive)

        from pm4py.evaluation.generalization import factory as generalization_factory

        generalization_alpha = generalization_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        generalization_inductive = generalization_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                                inductive_final_marking)

        # print("generalization_alpha=",generalization_alpha)
        # print("generalization_inductive=",generalization_inductive)

        from pm4py.evaluation.simplicity import factory as simplicity_factory

        simplicity_alpha = simplicity_factory.apply(alpha_petri)
        simplicity_inductive = simplicity_factory.apply(inductive_petri)

        # print("simplicity_alpha=",simplicity_alpha)
        # print("simplicity_inductive=",simplicity_inductive)

        from pm4py.evaluation import factory as evaluation_factory

        alpha_evaluation_result = evaluation_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        # print("alpha_evaluation_result=",alpha_evaluation_result)

        inductive_evaluation_result = evaluation_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                               inductive_final_marking)


if __name__ == "__main__":
    unittest.main()
