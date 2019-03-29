import os
import unittest

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.objects.log.util import prefix_matrix
from tests.constants import INPUT_DATA_DIR
from pm4py.objects.petri.projection import project_net_on_matrix
import numpy as np


class MatrixRepTest(unittest.TestCase):
    def test_rep_log_petri_fitness(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        pref_mat, var_mat, activities = prefix_matrix.get_prefix_variants_matrix(log)

        net, im, fm = alpha_miner.apply(log)

        net_matrix = project_net_on_matrix(net, activities)

        product_matrix = np.matmul(pref_mat, net_matrix)
        max_product_matrix = np.max(product_matrix)

        self.assertGreaterEqual(max_product_matrix, 0)
