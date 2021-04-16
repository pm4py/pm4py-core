import os
import unittest

import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.objects.process_tree.importer import importer as tree_importer
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.petri_net.exporter import exporter as petri_exporter
from pm4py.objects.process_tree.exporter import exporter as tree_exporter
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter


class ImpExpFromString(unittest.TestCase):
    def test_imp_xes_from_str(self):
        F = open(os.path.join("input_data", "running-example.xes"), "rb")
        content = F.read()
        F.close()
        log = xes_importer.deserialize(content)
        self.assertIsNotNone(log)

    def test_imp_petri_from_str(self):
        F = open(os.path.join("input_data", "running-example.pnml"), "rb")
        content = F.read()
        F.close()
        net, im, fm = petri_importer.deserialize(content)
        self.assertIsNotNone(net)
        self.assertIsNotNone(im)

    def test_imp_tree_from_str(self):
        F = open(os.path.join("input_data", "running-example.ptml"), "rb")
        content = F.read()
        F.close()
        tree = tree_importer.deserialize(content)
        self.assertIsNotNone(tree)

    def test_imp_bpmn_from_str(self):
        F = open(os.path.join("input_data", "running-example.bpmn"), "rb")
        content = F.read()
        F.close()
        bpmn_graph = bpmn_importer.deserialize(content)
        self.assertIsNotNone(bpmn_graph)

    def test_imp_xes_from_str2(self):
        F = open(os.path.join("input_data", "running-example.xes"), "r")
        content = F.read()
        F.close()
        log = xes_importer.deserialize(content)
        self.assertIsNotNone(log)

    def test_imp_petri_from_str2(self):
        F = open(os.path.join("input_data", "running-example.pnml"), "r")
        content = F.read()
        F.close()
        net, im, fm = petri_importer.deserialize(content)
        self.assertIsNotNone(net)
        self.assertIsNotNone(im)

    def test_imp_tree_from_str2(self):
        F = open(os.path.join("input_data", "running-example.ptml"), "r")
        content = F.read()
        F.close()
        tree = tree_importer.deserialize(content)
        self.assertIsNotNone(tree)

    def test_imp_bpmn_from_str2(self):
        F = open(os.path.join("input_data", "running-example.bpmn"), "r")
        content = F.read()
        F.close()
        bpmn_graph = bpmn_importer.deserialize(content)
        self.assertIsNotNone(bpmn_graph)

    def test_exp_xes_to_str(self):
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        xes_exporter.serialize(log)

    def test_exp_pnml_to_str(self):
        net, im, fm = pm4py.read_pnml(os.path.join("input_data", "running-example.pnml"))
        petri_exporter.serialize(net, im, fm)

    def test_exp_ptml_to_str(self):
        tree = pm4py.read_ptml(os.path.join("input_data", "running-example.ptml"))
        tree_exporter.serialize(tree)

    def test_exp_bpmn_to_str(self):
        bpmn_graph = pm4py.read_bpmn(os.path.join("input_data", "running-example.bpmn"))
        bpmn_exporter.serialize(bpmn_graph)


if __name__ == "__main__":
    unittest.main()
