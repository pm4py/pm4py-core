import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import csv as csv_importer
from pm4py.log.importer import xes as xes_importer
import pm4py.log.transform as log_transform
from pm4py.algo.alpha.versions import classic as alpha_classic
from pm4py.models.petri import visualize as pn_viz
from pm4py.algo.tokenreplay import token_replay
from pm4py.algo.tokenreplay.token_replay import NoConceptNameException
from pm4py.models import petri
from pm4py.models.petri.export import pnml as petri_exporter
from constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR
import logging

class AlphaMinerTest(unittest.TestCase):
	def obtainPetriNetThroughAlphaMiner(self, logName):
		if ".xes" in logName:
			traceLog = xes_importer.import_from_path_xes(logName)
		else:
			eventLog = csv_importer.import_from_path(logName)
			traceLog = log_transform.transform_event_log_to_trace_log(eventLog)
		net, marking = alpha_classic.apply(traceLog)
		return traceLog, net, marking
	
	def test_applyAlphaMinerToXES(self):
		# calculate and compare Petri nets obtained on the same log to verify that instances
		# are working correctly
		log1, net1, marking1 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		log2, net2, marking2 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		petri_exporter.export_petri_to_pnml(net1, marking1, os.path.join(OUTPUT_DATA_DIR,"running-example.pnml"))
		os.remove(os.path.join(OUTPUT_DATA_DIR,"running-example.pnml"))
		self.assertEqual(len(net1.places),len(net2.places))
		self.assertEqual(len(net1.transitions),len(net2.transitions))
		self.assertEqual(len(net1.arcs),len(net2.arcs))
		final_marking = petri.net.Marking()
		for p in net1.places:
			if not p.out_arcs:
				final_marking[p] = 1
		[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log1, net1, marking1, final_marking, enable_placeFitness=True)
		
	def test_applyAlphaMinerToCSV(self):
		# calculate and compare Petri nets obtained on the same log to verify that instances
		# are working correctly
		log1, net1, marking1 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.csv"))
		log1, net2, marking2 = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.csv"))
		petri_exporter.export_petri_to_pnml(net1, marking1, os.path.join(OUTPUT_DATA_DIR,"running-example.pnml"))
		os.remove(os.path.join(OUTPUT_DATA_DIR,"running-example.pnml"))
		self.assertEqual(len(net1.places),len(net2.places))
		self.assertEqual(len(net1.transitions),len(net2.transitions))
		self.assertEqual(len(net1.arcs),len(net2.arcs))
		final_marking = petri.net.Marking()
		for p in net1.places:
			if not p.out_arcs:
				final_marking[p] = 1
		[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log1, net1, marking1, final_marking, enable_placeFitness=True)
	
	def test_alphaMinerVisualizationFromXES(self):
		log, net, marking = self.obtainPetriNetThroughAlphaMiner(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		petri_exporter.export_petri_to_pnml(net, marking, os.path.join(OUTPUT_DATA_DIR,"running-example.pnml"))
		os.remove(os.path.join(OUTPUT_DATA_DIR,"running-example.pnml"))
		gviz = pn_viz.graphviz_visualization(net)
		final_marking = petri.net.Marking()
		for p in net.places:
			if not p.out_arcs:
				final_marking[p] = 1
		[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net, marking, final_marking, enable_placeFitness=True)
	
	def test_applyAlphaMinerToProblematicLogs(self):
		logs = os.listdir(PROBLEMATIC_XES_DIR)
		for log in logs:
			try:
				logFullPath = os.path.join(PROBLEMATIC_XES_DIR, log)
				# calculate and compare Petri nets obtained on the same log to verify that instances
				# are working correctly
				log1, net1, marking1 = self.obtainPetriNetThroughAlphaMiner(logFullPath)
				log2, net2, marking2 = self.obtainPetriNetThroughAlphaMiner(logFullPath)
				self.assertEqual(len(net1.places),len(net2.places))
				self.assertEqual(len(net1.transitions),len(net2.transitions))
				self.assertEqual(len(net1.arcs),len(net2.arcs))
				final_marking = petri.net.Marking()
				for p in net1.places:
					if not p.out_arcs:
						final_marking[p] = 1
				[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log1, net1, marking1, final_marking, enable_placeFitness=True)
			except SyntaxError as e:
				logging.info("SyntaxError on log "+str(log)+": "+str(e))
			except NoConceptNameException as e:
				logging.info("Concept name error on log "+str(log)+": "+str(e))

if __name__ == "__main__":
	unittest.main()