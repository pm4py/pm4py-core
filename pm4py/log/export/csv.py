from lxml import etree
import pm4py.log.instance as log_instance
import pm4py.log.transform as log_transform
import pandas as pd

def export_log(log, outputFilePath):
	"""
	Export a CSV log

	Parameters
	----------
	log
		Event log
	outputFilePath
		Output file path
	"""
	if type(log) is log_instance.TraceLog:
		log = log_transform.transform_trace_log_to_event_log(log)
	transfLog = [dict(x) for x in log]
	df = pd.DataFrame.from_dict(transfLog)
	df.to_csv(outputFilePath)