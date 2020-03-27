import os
import unittest


class DocMeasuresDocumentationTest(unittest.TestCase):
    def test_docmeasures11(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        from pm4py.objects.log.importer.xes import algorithm as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "receipt.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        alpha_petri, alpha_initial_marking, alpha_final_marking = alpha_miner.apply(log)
        inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)
        from pm4py.evaluation.replay_fitness import evaluator as replay_alg
        fitness_alpha = replay_alg.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking, variant=replay_alg.TOKEN_BASED)
        fitness_inductive = replay_alg.apply(log, inductive_petri, inductive_initial_marking,
                                                 inductive_final_marking, variant=replay_alg.TOKEN_BASED)
        del fitness_alpha
        del fitness_inductive
        from pm4py.evaluation.precision import evaluator as precision_alg
        precision_alpha = precision_alg.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking, variant=precision_alg.ETCONFORMANCE_TOKEN)
        precision_inductive = precision_alg.apply(log, inductive_petri, inductive_initial_marking,
                                                      inductive_final_marking, variant=precision_alg.ETCONFORMANCE_TOKEN)
        del precision_alpha
        del precision_inductive
        from pm4py.evaluation.generalization import evaluator as generalization
        generalization_alpha = generalization.apply(log, alpha_petri, alpha_initial_marking,
                                                            alpha_final_marking)
        generalization_inductive = generalization.apply(log, inductive_petri, inductive_initial_marking,
                                                                inductive_final_marking)
        del generalization_alpha
        del generalization_inductive
        from pm4py.evaluation.simplicity import evaluator as simplicity
        simplicity_alpha = simplicity.apply(alpha_petri)
        simplicity_inductive = simplicity.apply(inductive_petri)
        del simplicity_alpha
        del simplicity_inductive
        from pm4py.evaluation import algorithm as evaluation_alg
        alpha_evaluation_result = evaluation_alg.apply(log, alpha_petri, alpha_initial_marking, alpha_final_marking)
        inductive_evaluation_result = evaluation_alg.apply(log, inductive_petri, inductive_initial_marking,
                                                               inductive_final_marking)
        del alpha_evaluation_result
        del inductive_evaluation_result


if __name__ == "__main__":
    unittest.main()
