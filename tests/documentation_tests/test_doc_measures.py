import os
import unittest


class DocMeasuresDocumentationTest(unittest.TestCase):
    def test_docmeasures11(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        from pm4py.objects.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "receipt.xes"))
        from pm4py.algo.discovery.alpha import factory as alpha_miner
        from pm4py.algo.discovery.inductive import factory as inductive_miner
        alpha_petri, alpha_initial_marking, alpha_final_marking = alpha_miner.apply(log)
        inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)
        from pm4py.evaluation.replay_fitness import factory as replay_factory
        fitness_alpha = replay_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        fitness_inductive = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                 inductive_final_marking)
        del fitness_alpha
        del fitness_inductive
        from pm4py.evaluation.precision import factory as precision_factory
        precision_alpha = precision_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        precision_inductive = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                      inductive_final_marking)
        del precision_alpha
        del precision_inductive
        from pm4py.evaluation.generalization import factory as generalization_factory
        generalization_alpha = generalization_factory.apply(log, alpha_petri, alpha_initial_marking,
                                                            alpha_final_marking)
        generalization_inductive = generalization_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                                inductive_final_marking)
        del generalization_alpha
        del generalization_inductive
        from pm4py.evaluation.simplicity import factory as simplicity_factory
        simplicity_alpha = simplicity_factory.apply(alpha_petri)
        simplicity_inductive = simplicity_factory.apply(inductive_petri)
        del simplicity_alpha
        del simplicity_inductive
        from pm4py.evaluation import factory as evaluation_factory
        alpha_evaluation_result = evaluation_factory.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        inductive_evaluation_result = evaluation_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                               inductive_final_marking)
        del alpha_evaluation_result
        del inductive_evaluation_result


if __name__ == "__main__":
    unittest.main()
