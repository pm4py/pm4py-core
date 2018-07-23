import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import csv as csv_importer
from pm4py.log.importer import xes as xes_importer
import pm4py.log.transform as log_transform
from pm4py.algo.alpha import classic as alpha_classic
from pm4py.models.petri import visualize as pn_viz
from constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR

class AlphaMinerTest(unittest.TestCase):
	def obtainPetriNetThroughAlphaMiner(self, logName):
		if ".xes" in logName:
			traceLog = xes_importer.import_from_path_xes(logName)
		else:
			eventLog = csv_importer.import_from_path(logName)
			traceLog = log_transform.transform_event_log_to_trace_log(eventLog)
		net = alpha_classic.apply(traceLog)
		return net
	
	def test_applyAlphaMinerToXES(self):
		# calculate and compare Petri nets obtained on the same log to verify that instances
		# are working correctly
		net1 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		net2 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		self.assertEqual(len(net1.places),len(net2.places))
		self.assertEqual(len(net1.transitions),len(net2.transitions))
		self.assertEqual(len(net1.arcs),len(net2.arcs))
		
	def test_applyAlphaMinerToCSV(self):
		# calculate and compare Petri nets obtained on the same log to verify that instances
		# are working correctly
		net1 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.csv"))
		net2 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.csv"))
		self.assertEqual(len(net1.places),len(net2.places))
		self.assertEqual(len(net1.transitions),len(net2.transitions))
		self.assertEqual(len(net1.arcs),len(net2.arcs))
	
	def test_alphaMinerVisualizationFromXES(self):
		net = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		gviz = pn_viz.graphviz_visualization(net)
	
	def test_applyAlphaMinerToProblematicLogs(self):
		logs = os.listdir(PROBLEMATIC_XES_DIR)
		for log in logs:
			logFullPath = os.path.join(PROBLEMATIC_XES_DIR, log)
			# calculate and compare Petri nets obtained on the same log to verify that instances
			# are working correctly
			net1 = self.obtainPetriNetThroughAlphaMiner(logFullPath)
			net2 = self.obtainPetriNetThroughAlphaMiner(logFullPath)
			self.assertEqual(len(net1.places),len(net2.places))
			self.assertEqual(len(net1.transitions),len(net2.transitions))
			self.assertEqual(len(net1.arcs),len(net2.arcs))

if __name__ == "__main__":
	unittest.main()